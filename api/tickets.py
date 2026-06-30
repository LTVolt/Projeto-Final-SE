from uuid import UUID

from supabase import Client

from api.schemas import TicketOut, UserOut


class DatabaseError(RuntimeError):
    """Erro de acesso ao Supabase que pode ser traduzido pela camada HTTP."""


class TicketRepository:
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

    def list_tickets_for_user(self, user_id: UUID) -> list[TicketOut]:
        fields = (
            "id,description,status,opened_at,resolved_at,"
            "category:categories!tickets_category_id_fkey(name),"
            "opened_by_user:users!tickets_opened_by_fkey(name),"
            "handled_by_user:users!tickets_handled_by_fkey(name)"
        )

        try:
            response = (
                self.client.table("tickets")
                .select(fields)
                .eq("opened_by", str(user_id))
                .order("opened_at", desc=True)
                .execute()
            )
        except Exception as exc:
            raise DatabaseError("Falha ao consultar tickets.") from exc

        return [self._to_ticket(row) for row in response.data]

    @staticmethod
    def _to_ticket(row: dict) -> TicketOut:
        category = row.get("category") or {}
        opened_by_user = row.get("opened_by_user") or {}
        handled_by_user = row.get("handled_by_user") or {}

        return TicketOut(
            id=row["id"],
            description=row["description"],
            status=row["status"],
            opened_at=row["opened_at"],
            resolved_at=row.get("resolved_at"),
            category=category.get("name", "Sem categoria"),
            opened_by=opened_by_user.get("name", "Utilizador desconhecido"),
            handled_by=handled_by_user.get("name"),
        )
