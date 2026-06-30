from collections import Counter
from uuid import UUID

from supabase import Client

from api.schemas import (
    CategoryMetric,
    CategoryOut,
    MetricsOut,
    SolutionOut,
    TicketOut,
    TicketView,
    UserOut,
)


class DatabaseError(RuntimeError):
    """Erro de acesso ao Supabase traduzido pela camada HTTP."""


class TicketRepository:
    ticket_fields = (
        "id,category_id,opened_by,handled_by,description,status,opened_at,resolved_at,resolution_note,"
        "category:categories!tickets_category_id_fkey(name),"
        "opened_by_user:users!tickets_opened_by_fkey(name),"
        "handled_by_user:users!tickets_handled_by_fkey(name)"
    )

    def __init__(self, client: Client) -> None:
        self.client = client

    def list_users(self) -> list[UserOut]:
        try:
            response = (
                self.client.table("users")
                .select("id,name,type,department,permission")
                .order("name")
                .execute()
            )
        except Exception as exc:
            raise DatabaseError("Falha ao consultar utilizadores.") from exc
        return [UserOut.model_validate(row) for row in response.data]

    def get_user(self, user_id: UUID) -> UserOut | None:
        try:
            response = (
                self.client.table("users")
                .select("id,name,type,department,permission")
                .eq("id", str(user_id))
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise DatabaseError("Falha ao consultar o utilizador.") from exc
        return UserOut.model_validate(response.data[0]) if response.data else None

    def list_categories(self) -> list[CategoryOut]:
        try:
            response = (
                self.client.table("categories")
                .select("id,name,description")
                .order("name")
                .execute()
            )
        except Exception as exc:
            raise DatabaseError("Falha ao consultar categorias.") from exc
        return [CategoryOut.model_validate(row) for row in response.data]

    def get_category(self, category_id: UUID) -> CategoryOut | None:
        try:
            response = (
                self.client.table("categories")
                .select("id,name,description")
                .eq("id", str(category_id))
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise DatabaseError("Falha ao consultar a categoria.") from exc
        return CategoryOut.model_validate(response.data[0]) if response.data else None

    def list_solutions(self) -> list[SolutionOut]:
        fields = (
            "id,category_id,title,symptoms,resolution_steps,created_at,"
            "category:categories!solutions_category_id_fkey(name)"
        )
        try:
            response = (
                self.client.table("solutions")
                .select(fields)
                .order("title")
                .execute()
            )
        except Exception as exc:
            raise DatabaseError("Falha ao consultar soluções.") from exc

        solutions = []
        for row in response.data:
            category = row.get("category") or {}
            solutions.append(
                SolutionOut(
                    id=row["id"],
                    category_id=row["category_id"],
                    category=category.get("name", "Sem categoria"),
                    title=row["title"],
                    symptoms=row["symptoms"],
                    resolution_steps=row["resolution_steps"],
                    created_at=row["created_at"],
                )
            )
        return solutions

    def list_tickets(self, view: TicketView, current_user: UserOut) -> list[TicketOut]:
        try:
            query = self.client.table("tickets").select(self.ticket_fields)
            if current_user.type == "common":
                query = query.eq("opened_by", str(current_user.id))
            if view == "assigned":
                query = query.eq("handled_by", str(current_user.id)).eq(
                    "status", "in_progress"
                )
            elif view == "open":
                query = query.in_("status", ["open", "in_progress"])
            elif view == "history":
                query = query.eq("status", "closed")
            response = query.order("opened_at", desc=True).execute()
        except Exception as exc:
            raise DatabaseError("Falha ao consultar tickets.") from exc
        return [self._to_ticket(row) for row in response.data]

    def get_ticket(self, ticket_id: UUID) -> TicketOut | None:
        try:
            response = (
                self.client.table("tickets")
                .select(self.ticket_fields)
                .eq("id", str(ticket_id))
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise DatabaseError("Falha ao consultar o ticket.") from exc
        return self._to_ticket(response.data[0]) if response.data else None

    def create_ticket(self, values: dict) -> TicketOut:
        try:
            response = self.client.table("tickets").insert(values).execute()
        except Exception as exc:
            raise DatabaseError("Falha ao criar o ticket.") from exc
        return self._require_ticket(response.data[0]["id"])

    def update_ticket(self, ticket_id: UUID, values: dict) -> TicketOut:
        try:
            self.client.table("tickets").update(values).eq("id", str(ticket_id)).execute()
        except Exception as exc:
            raise DatabaseError("Falha ao atualizar o ticket.") from exc
        return self._require_ticket(ticket_id)

    def delete_ticket(self, ticket_id: UUID) -> None:
        try:
            self.client.table("tickets").delete().eq("id", str(ticket_id)).execute()
        except Exception as exc:
            raise DatabaseError("Falha ao eliminar o ticket.") from exc

    def get_metrics(self) -> MetricsOut:
        admin_view = UserOut(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="Metrics",
            type="admin",
            department="System",
            permission="Metrics",
        )
        tickets = self.list_tickets("all", admin_view)
        users = self.list_users()
        status_counts = Counter(ticket.status for ticket in tickets)
        category_counts = Counter(
            (ticket.category_id, ticket.category) for ticket in tickets
        )
        active_users = {
            ticket.opened_by_id
            for ticket in tickets
            if ticket.status in {"open", "in_progress"}
        }

        return MetricsOut(
            active_tickets=status_counts["open"] + status_counts["in_progress"],
            users_with_active_tickets=len(active_users),
            helpdesk_users=sum(user.type == "helpdesk" for user in users),
            by_status={
                "open": status_counts["open"],
                "in_progress": status_counts["in_progress"],
                "closed": status_counts["closed"],
            },
            by_category=[
                CategoryMetric(category_id=category_id, category=name, count=count)
                for (category_id, name), count in sorted(
                    category_counts.items(), key=lambda item: item[0][1]
                )
            ],
        )

    def _require_ticket(self, ticket_id: UUID | str) -> TicketOut:
        ticket = self.get_ticket(UUID(str(ticket_id)))
        if ticket is None:
            raise DatabaseError("O ticket escrito não pôde ser relido.")
        return ticket

    @staticmethod
    def _to_ticket(row: dict) -> TicketOut:
        category = row.get("category") or {}
        opened_by_user = row.get("opened_by_user") or {}
        handled_by_user = row.get("handled_by_user") or {}
        return TicketOut(
            id=row["id"],
            category_id=row["category_id"],
            category=category.get("name", "Sem categoria"),
            opened_by_id=row["opened_by"],
            opened_by=opened_by_user.get("name", "Utilizador desconhecido"),
            handled_by_id=row.get("handled_by"),
            handled_by=handled_by_user.get("name"),
            description=row["description"],
            status=row["status"],
            opened_at=row["opened_at"],
            resolved_at=row.get("resolved_at"),
            resolution_note=row.get("resolution_note"),
        )
