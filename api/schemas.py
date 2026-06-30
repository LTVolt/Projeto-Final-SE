from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: Literal["common", "helpdesk", "admin"]
    department: str
    permission: str


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    description: str
    status: Literal["open", "in_progress", "closed"]
    opened_at: datetime
    resolved_at: datetime | None
    category: str
    opened_by: str
    handled_by: str | None
