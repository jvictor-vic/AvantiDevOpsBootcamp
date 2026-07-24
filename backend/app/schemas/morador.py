import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class MoradorBase(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    telefone: str | None = None
    tipo: str = "proprietario"
    apartamento_id: int

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        pattern = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
        if not re.match(pattern, v):
            raise ValueError("CPF deve seguir o formato 000.000.000-00")
        return v

    @field_validator("tipo")
    @classmethod
    def validate_tipo(cls, v: str) -> str:
        allowed = {"proprietario", "inquilino", "sindico"}
        if v not in allowed:
            raise ValueError(f"tipo deve ser um de: {', '.join(sorted(allowed))}")
        return v


class MoradorCreate(MoradorBase):
    pass


class MoradorUpdate(BaseModel):
    nome: str | None = None
    cpf: str | None = None
    email: EmailStr | None = None
    telefone: str | None = None
    tipo: str | None = None

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v: str | None) -> str | None:
        if v is not None and v.strip():
            pattern = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
            if not re.match(pattern, v):
                raise ValueError("CPF deve seguir o formato 000.000.000-00")
        return v

    @field_validator("tipo")
    @classmethod
    def validate_tipo(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"proprietario", "inquilino", "sindico"}
            if v not in allowed:
                raise ValueError(
                    f"tipo deve ser um de: {', '.join(sorted(allowed))}"
                )
        return v


class MoradorRead(MoradorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
