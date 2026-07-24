"""WebSocket message schemas for real-time Ocorrencia feed."""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    OCORRENCIA_CRIADA = "ocorrencia_criada"
    OCORRENCIA_ATUALIZADA = "ocorrencia_atualizada"
    OCORRENCIA_REMOVIDA = "ocorrencia_removida"
    PING = "ping"
    PONG = "pong"


class WSMessage(BaseModel):
    """Base WebSocket message envelope."""

    type: EventType
    data: dict | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

