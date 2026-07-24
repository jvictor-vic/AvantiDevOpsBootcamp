"""REST endpoints for Rivalidade CRUD."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.rivalidade import RivalidadeRepository
from app.schemas.rivalidade import RivalidadeCreate, RivalidadeRead, RivalidadeUpdate
from app.services.rivalidade import (
    NivelInvalido,
    RivalidadeJaExiste,
    RivalidadeNaoEncontrada,
    RivalidadeService,
)

router = APIRouter(prefix="/rivalidades", tags=["rivalidades"])


async def _get_service(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> RivalidadeService:
    return RivalidadeService(RivalidadeRepository(session))


@router.get("/", response_model=list[RivalidadeRead])
async def listar(service: Annotated[RivalidadeService, Depends(_get_service)]):
    return await service.listar()


@router.get("/por-apartamento/{apartamento_id}", response_model=list[RivalidadeRead])
async def listar_por_apartamento(
    apartamento_id: int,
    service: Annotated[RivalidadeService, Depends(_get_service)],
):
    return await service.listar_por_apartamento(apartamento_id)


@router.get("/top", response_model=list[RivalidadeRead])
async def top(
    service: Annotated[RivalidadeService, Depends(_get_service)],
    limite: int = Query(10, ge=1, le=100),
):
    return await service.top_rivalidades(limite)


@router.get("/{rivalidade_id}", response_model=RivalidadeRead)
async def obter(
    rivalidade_id: int,
    service: Annotated[RivalidadeService, Depends(_get_service)],
):
    try:
        return await service.buscar(rivalidade_id)
    except RivalidadeNaoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=RivalidadeRead, status_code=status.HTTP_201_CREATED)
async def criar(
    data: RivalidadeCreate,
    service: Annotated[RivalidadeService, Depends(_get_service)],
):
    try:
        return await service.criar(
            apartamento_a_id=data.apartamento_a_id,
            apartamento_b_id=data.apartamento_b_id,
            motivo=data.motivo,
            nivel=data.nivel,
        )
    except (RivalidadeJaExiste, NivelInvalido) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{rivalidade_id}/escalar", response_model=RivalidadeRead)
async def escalar(
    rivalidade_id: int,
    service: Annotated[RivalidadeService, Depends(_get_service)],
):
    try:
        return await service.escalar(rivalidade_id)
    except RivalidadeNaoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{rivalidade_id}", response_model=RivalidadeRead)
async def atualizar(
    rivalidade_id: int,
    data: RivalidadeUpdate,
    service: Annotated[RivalidadeService, Depends(_get_service)],
):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar",
        )
    try:
        return await service.atualizar(rivalidade_id, update_data)
    except RivalidadeNaoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NivelInvalido as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{rivalidade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover(
    rivalidade_id: int,
    service: Annotated[RivalidadeService, Depends(_get_service)],
):
    try:
        await service.remover(rivalidade_id)
    except RivalidadeNaoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
