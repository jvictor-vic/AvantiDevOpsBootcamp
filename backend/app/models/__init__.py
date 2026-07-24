from app.database import Base
from app.models.apartamento import Apartamento
from app.models.condominio import Condominio
from app.models.morador import Morador
from app.models.ocorrencia import Ocorrencia
from app.models.rivalidade import Rivalidade

__all__ = [
    "Apartamento",
    "Base",
    "Condominio",
    "Morador",
    "Ocorrencia",
    "Rivalidade",
]
