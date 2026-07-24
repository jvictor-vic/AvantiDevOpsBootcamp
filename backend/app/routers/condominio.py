"""REST endpoints for Condominio CRUD."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.condominio import CondominioRepository
from app.schemas.condominio import CondominioCreate, CondominioRead, CondominioUpdate
from app.services.condominio import (
    CondominioJaExiste,
    CondominioNaoEncontrado,
    CondominioService,
)

router = APIRouter(prefix="/condominios", tags=["condominios"])


async def _get_service(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> CondominioService:
    return CondominioService(CondominioRepository(session))


@router.get("/", response_model=list[CondominioRead])
async def listar(service: Annotated[CondominioService, Depends(_get_service)]):
    """Lista todos os condomínios cadastrados."""
    return await service.listar()


@router.get("/{condominio_id}", response_model=CondominioRead)
async def obter(
    condominio_id: int,
    service: Annotated[CondominioService, Depends(_get_service)],
):
    """Obtém um condomínio pelo ID."""
    try:
        return await service.buscar(condominio_id)
    except CondominioNaoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Condomínio {condominio_id} não encontrado",
        )


@router.post("/", response_model=CondominioRead, status_code=status.HTTP_201_CREATED)
async def criar(
    data: CondominioCreate,
    service: Annotated[CondominioService, Depends(_get_service)],
):
    """Cria um novo condomínio."""
    try:
        return await service.criar(data)
    except CondominioJaExiste as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.put("/{condominio_id}", response_model=CondominioRead)
async def atualizar(
    condominio_id: int,
    data: CondominioUpdate,
    service: Annotated[CondominioService, Depends(_get_service)],
):
    """Atualiza um condomínio existente."""
    try:
        return await service.atualizar(condominio_id, data)
    except CondominioNaoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Condomínio {condominio_id} não encontrado",
        )
    except CondominioJaExiste as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.delete("/{condominio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover(
    condominio_id: int,
    service: Annotated[CondominioService, Depends(_get_service)],
):
    """Remove um condomínio."""
    try:
        await service.remover(condominio_id)
    except CondominioNaoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Condomínio {condominio_id} não encontrado",
        )
