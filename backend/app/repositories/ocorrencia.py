from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ocorrencia import Ocorrencia


class OcorrenciaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, ocorrencia: Ocorrencia) -> Ocorrencia:
        self.session.add(ocorrencia)
        await self.session.commit()
        await self.session.refresh(ocorrencia)
        return ocorrencia

    async def get_by_id(self, ocorrencia_id: int) -> Ocorrencia | None:
        result = await self.session.execute(
            select(Ocorrencia).where(Ocorrencia.id == ocorrencia_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        categoria: str | None = None,
        status: str | None = None,
        gravidade: str | None = None,
        apartamento_id: int | None = None,
    ) -> list[Ocorrencia]:
        stmt = (
            select(Ocorrencia)
            .order_by(Ocorrencia.created_at.desc())
        )
        if categoria is not None:
            stmt = stmt.where(Ocorrencia.categoria == categoria)
        if status is not None:
            stmt = stmt.where(Ocorrencia.status == status)
        if gravidade is not None:
            stmt = stmt.where(Ocorrencia.gravidade == gravidade)
        if apartamento_id is not None:
            stmt = stmt.where(Ocorrencia.apartamento_id == apartamento_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recentes(self) -> list[Ocorrencia]:
        limite = datetime.now(UTC) - timedelta(hours=24)
        result = await self.session.execute(
            select(Ocorrencia)
            .where(Ocorrencia.created_at >= limite)
            .order_by(Ocorrencia.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, ocorrencia_id: int, dados: dict) -> Ocorrencia | None:
        ocorrencia = await self.get_by_id(ocorrencia_id)
        if ocorrencia is None:
            return None
        for key, value in dados.items():
            setattr(ocorrencia, key, value)
        await self.session.commit()
        await self.session.refresh(ocorrencia)
        return ocorrencia

    async def delete(self, ocorrencia_id: int) -> bool:
        ocorrencia = await self.get_by_id(ocorrencia_id)
        if ocorrencia is None:
            return False
        await self.session.delete(ocorrencia)
        await self.session.commit()
        return True
