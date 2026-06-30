from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

UserType = Literal["common", "helpdesk", "admin"]
TicketStatus = Literal["open", "in_progress", "closed"]
TicketView = Literal["open", "history", "all"]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: UserType
    department: str
    permission: str


class CategoryOut(BaseModel):
    id: UUID
    name: str
    description: str


class SolutionOut(BaseModel):
    id: UUID
    category_id: UUID
    category: str
    title: str
    symptoms: str
    resolution_steps: str
    created_at: datetime


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    category: str
    opened_by_id: UUID
    opened_by: str
    handled_by_id: UUID | None
    handled_by: str | None
    description: str
    status: TicketStatus
    opened_at: datetime
    resolved_at: datetime | None


class TicketCreate(BaseModel):
    category_id: UUID
    description: str = Field(min_length=5, max_length=2000)
    opened_by: UUID | None = None
    handled_by: UUID | None = None
    status: TicketStatus = "open"


class TicketUpdate(BaseModel):
    category_id: UUID | None = None
    opened_by: UUID | None = None
    handled_by: UUID | None = None
    description: str | None = Field(default=None, min_length=5, max_length=2000)
    status: TicketStatus | None = None

    @model_validator(mode="after")
    def require_change(self) -> "TicketUpdate":
        if not self.model_fields_set:
            raise ValueError("É necessário indicar pelo menos uma alteração.")
        return self


class CategoryMetric(BaseModel):
    category_id: UUID
    category: str
    count: int


class MetricsOut(BaseModel):
    active_tickets: int
    users_with_active_tickets: int
    helpdesk_users: int
    by_status: dict[TicketStatus, int]
    by_category: list[CategoryMetric]
