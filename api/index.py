from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import get_settings
from api.database import get_supabase
from api.schemas import (
    CategoryOut,
    MetricsOut,
    SolutionOut,
    TicketCreate,
    TicketOut,
    TicketUpdate,
    TicketView,
    UserOut,
)
from api.tickets import DatabaseError, TicketRepository

settings = get_settings()

app = FastAPI(title="Streamlined Ticket System API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.public_app_url).rstrip("/")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_repository() -> TicketRepository:
    return TicketRepository(get_supabase())


def get_current_user(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> UserOut:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="É necessário escolher um utilizador.")
    try:
        user_id = UUID(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="O utilizador indicado não é válido.") from exc

    user = get_repository().get_user(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="O utilizador indicado não existe.")
    return user


CurrentUser = Annotated[UserOut, Depends(get_current_user)]


@app.exception_handler(DatabaseError)
async def database_error_handler(_: Request, __: DatabaseError) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": "Não foi possível comunicar com a base de dados."},
    )


def require_role(user: UserOut, *roles: str) -> None:
    if user.type not in roles:
        raise HTTPException(status_code=403, detail="Não tem permissão para esta ação.")


def require_ticket_access(user: UserOut, ticket: TicketOut) -> None:
    if user.type == "common" and ticket.opened_by_id != user.id:
        raise HTTPException(status_code=403, detail="Não tem acesso a este ticket.")


def require_category(repository: TicketRepository, category_id: UUID) -> None:
    if repository.get_category(category_id) is None:
        raise HTTPException(status_code=409, detail="A categoria indicada não existe.")


def require_user(
    repository: TicketRepository,
    user_id: UUID,
    *,
    helpdesk_only: bool = False,
) -> UserOut:
    user = repository.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=409, detail="O utilizador indicado não existe.")
    if helpdesk_only and user.type != "helpdesk":
        raise HTTPException(status_code=409, detail="O responsável deve ser helpdesk.")
    return user


@app.get("/api/users", response_model=list[UserOut])
def list_users() -> list[UserOut]:
    return get_repository().list_users()


@app.get("/api/categories", response_model=list[CategoryOut])
def list_categories(_: CurrentUser) -> list[CategoryOut]:
    return get_repository().list_categories()


@app.get("/api/solutions", response_model=list[SolutionOut])
def list_solutions(_: CurrentUser) -> list[SolutionOut]:
    return get_repository().list_solutions()


@app.get("/api/tickets", response_model=list[TicketOut])
def list_tickets(
    current_user: CurrentUser,
    view: TicketView = Query(default="open"),
) -> list[TicketOut]:
    return get_repository().list_tickets(view, current_user)


@app.get("/api/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: UUID, current_user: CurrentUser) -> TicketOut:
    ticket = get_repository().get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket não encontrado.")
    require_ticket_access(current_user, ticket)
    return ticket


@app.post("/api/tickets", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketCreate, current_user: CurrentUser) -> TicketOut:
    require_role(current_user, "common", "admin")
    repository = get_repository()
    require_category(repository, payload.category_id)

    if current_user.type == "common":
        values = {
            "category_id": str(payload.category_id),
            "opened_by": str(current_user.id),
            "handled_by": None,
            "description": payload.description.strip(),
            "status": "open",
            "resolved_at": None,
        }
        return repository.create_ticket(values)

    opened_by = payload.opened_by or current_user.id
    require_user(repository, opened_by)
    if payload.status == "open" and payload.handled_by is not None:
        raise HTTPException(status_code=409, detail="Um ticket aberto não pode ter responsável.")
    if payload.status != "open" and payload.handled_by is None:
        raise HTTPException(status_code=409, detail="Este estado exige um responsável.")
    if payload.handled_by is not None:
        require_user(repository, payload.handled_by, helpdesk_only=True)

    values = {
        "category_id": str(payload.category_id),
        "opened_by": str(opened_by),
        "handled_by": str(payload.handled_by) if payload.handled_by else None,
        "description": payload.description.strip(),
        "status": payload.status,
        "resolved_at": (
            datetime.now(timezone.utc).isoformat()
            if payload.status == "closed"
            else None
        ),
    }
    return repository.create_ticket(values)


@app.patch("/api/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: UUID,
    payload: TicketUpdate,
    current_user: CurrentUser,
) -> TicketOut:
    require_role(current_user, "admin")
    repository = get_repository()
    ticket = repository.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket não encontrado.")

    changes = payload.model_dump(exclude_unset=True)
    if "category_id" in changes:
        require_category(repository, changes["category_id"])
    if "opened_by" in changes:
        require_user(repository, changes["opened_by"])

    resulting_status = changes.get("status", ticket.status)
    resulting_handler = changes.get("handled_by", ticket.handled_by_id)
    if resulting_status == "open" and resulting_handler is not None:
        raise HTTPException(status_code=409, detail="Um ticket aberto não pode ter responsável.")
    if resulting_status != "open" and resulting_handler is None:
        raise HTTPException(status_code=409, detail="Este estado exige um responsável.")
    if resulting_handler is not None:
        require_user(repository, resulting_handler, helpdesk_only=True)

    values = {
        key: str(value) if isinstance(value, UUID) else value
        for key, value in changes.items()
    }
    if "description" in values:
        values["description"] = values["description"].strip()
    if resulting_status == "closed":
        if ticket.status != "closed":
            values["resolved_at"] = datetime.now(timezone.utc).isoformat()
    else:
        values["resolved_at"] = None
    return repository.update_ticket(ticket_id, values)


@app.delete("/api/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: UUID, current_user: CurrentUser) -> Response:
    require_role(current_user, "admin")
    repository = get_repository()
    if repository.get_ticket(ticket_id) is None:
        raise HTTPException(status_code=404, detail="Ticket não encontrado.")
    repository.delete_ticket(ticket_id)
    return Response(status_code=204)


@app.post("/api/tickets/{ticket_id}/assign", response_model=TicketOut)
def assign_ticket(ticket_id: UUID, current_user: CurrentUser) -> TicketOut:
    require_role(current_user, "helpdesk")
    repository = get_repository()
    ticket = repository.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket não encontrado.")
    if ticket.status == "closed":
        raise HTTPException(status_code=409, detail="Um ticket fechado não pode ser atribuído.")
    if ticket.handled_by_id == current_user.id and ticket.status == "in_progress":
        return ticket
    if ticket.handled_by_id is not None:
        raise HTTPException(status_code=409, detail="O ticket já está atribuído.")
    return repository.update_ticket(
        ticket_id,
        {"handled_by": str(current_user.id), "status": "in_progress"},
    )


@app.post("/api/tickets/{ticket_id}/close", response_model=TicketOut)
def close_ticket(ticket_id: UUID, current_user: CurrentUser) -> TicketOut:
    require_role(current_user, "helpdesk")
    repository = get_repository()
    ticket = repository.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket não encontrado.")
    if ticket.handled_by_id != current_user.id:
        raise HTTPException(status_code=409, detail="Só o helpdesk responsável pode fechar o ticket.")
    if ticket.status == "closed":
        return ticket
    if ticket.status != "in_progress":
        raise HTTPException(status_code=409, detail="O ticket deve estar em resolução.")
    return repository.update_ticket(
        ticket_id,
        {
            "status": "closed",
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.get("/api/metrics", response_model=MetricsOut)
def get_metrics(current_user: CurrentUser) -> MetricsOut:
    require_role(current_user, "admin")
    return get_repository().get_metrics()
