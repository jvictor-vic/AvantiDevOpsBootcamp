import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class CondominioBase(BaseModel):
    nome: str
    endereco: str
    cnpj: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v: str | None) -> str | None:
        if v is not None and v.strip():
            pattern = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"
            if not re.match(pattern, v):
                raise ValueError("CNPJ deve seguir o formato 00.000.000/0000-00")
        return v


class CondominioCreate(CondominioBase):
    pass


class CondominioUpdate(BaseModel):
    nome: str | None = None
    endereco: str | None = None
    cnpj: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v: str | None) -> str | None:
        if v is not None and v.strip():
            pattern = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"
            if not re.match(pattern, v):
                raise ValueError("CNPJ deve seguir o formato 00.000.000/0000-00")
        return v


class CondominioRead(CondominioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
