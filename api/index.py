from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_settings
from api.database import get_supabase
from api.schemas import TicketOut, UserOut
from api.tickets import DatabaseError, TicketRepository

settings = get_settings()

app = FastAPI(
    title="Streamlined Ticket System API",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.public_app_url).rstrip("/")],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_repository() -> TicketRepository:
    return TicketRepository(get_supabase())


@app.get("/api/users", response_model=list[UserOut])
def list_users() -> list[UserOut]:
    try:
        return get_repository().list_users()
    except DatabaseError as exc:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível consultar os utilizadores.",
        ) from exc


@app.get("/api/tickets", response_model=list[TicketOut])
def list_tickets(user_id: UUID) -> list[TicketOut]:
    try:
        return get_repository().list_tickets_for_user(user_id)
    except DatabaseError as exc:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível consultar os tickets.",
        ) from exc
