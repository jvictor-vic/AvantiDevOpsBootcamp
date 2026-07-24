"""Repository for Condominio CRUD operations."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.condominio import Condominio
from app.schemas.condominio import CondominioCreate, CondominioUpdate


class CondominioRepository:
    """Gerencia operações de banco para Condominio."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: CondominioCreate) -> Condominio:
        condominio = Condominio(**data.model_dump())
        self.session.add(condominio)
        await self.session.commit()
        await self.session.refresh(condominio)
        return condominio

    async def get_by_id(self, condominio_id: int) -> Condominio | None:
        result = await self.session.execute(
            select(Condominio).where(Condominio.id == condominio_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[Condominio]:
        result = await self.session.execute(select(Condominio))
        return result.scalars().all()

    async def get_by_cnpj(self, cnpj: str) -> Condominio | None:
        result = await self.session.execute(
            select(Condominio).where(Condominio.cnpj == cnpj)
        )
        return result.scalar_one_or_none()

    async def update(
        self, condominio_id: int, data: CondominioUpdate
    ) -> Condominio | None:
        condominio = await self.get_by_id(condominio_id)
        if condominio is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(condominio, key, value)
        await self.session.commit()
        await self.session.refresh(condominio)
        return condominio

    async def delete(self, condominio_id: int) -> bool:
        condominio = await self.get_by_id(condominio_id)
        if condominio is None:
            return False
        self.session.delete(condominio)
        await self.session.commit()
        return True
