"""REST endpoints for Ocorrencia CRUD with WebSocket broadcast."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.ocorrencia import OcorrenciaRepository
from app.schemas.ocorrencia import OcorrenciaCreate, OcorrenciaRead, OcorrenciaUpdate
from app.schemas.ws_message import EventType, WSMessage
from app.services.ocorrencia import (
    OcorrenciaNaoEncontrada,
    OcorrenciaService,
    TransicaoStatusInvalida,
)
from app.services.ws_manager import manager

router = APIRouter(prefix="/ocorrencias", tags=["ocorrencias"])


async def _get_service(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> OcorrenciaService:
    return OcorrenciaService(OcorrenciaRepository(session))


async def _broadcast_event(
    event_type: EventType, data: dict, ocorrencia_id: int | None = None
) -> None:
    message = WSMessage(type=event_type, data=data)
    await manager.broadcast(message)


@router.get("/", response_model=list[OcorrenciaRead])
async def listar(
    service: Annotated[OcorrenciaService, Depends(_get_service)],
    categoria: str | None = Query(None),
    status: str | None = Query(None),
    gravidade: str | None = Query(None),
    apartamento_id: int | None = Query(None),
):
    """Lista ocorrências com filtros opcionais."""
    return await service.listar(categoria, status, gravidade, apartamento_id)


@router.get("/recentes", response_model=list[OcorrenciaRead])
async def recentes(service: Annotated[OcorrenciaService, Depends(_get_service)]):
    """Retorna ocorrências dos últimos 24h."""
    return await service.listar_recentes()


@router.get("/{ocorrencia_id}", response_model=OcorrenciaRead)
async def obter(
    ocorrencia_id: int,
    service: Annotated[OcorrenciaService, Depends(_get_service)],
):
    try:
        return await service.buscar(ocorrencia_id)
    except OcorrenciaNaoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=OcorrenciaRead, status_code=status.HTTP_201_CREATED)
async def criar(
    data: OcorrenciaCreate,
    service: Annotated[OcorrenciaService, Depends(_get_service)],
):
    ocorrencia = await service.criar(
        titulo=data.titulo,
        descricao=data.descricao,
        categoria=data.categoria,
        apartamento_id=data.apartamento_id,
        gravidade=data.gravidade,
        status=data.status,
    )
    await _broadcast_event(
        EventType.OCORRENCIA_CRIADA,
        {"ocorrencia_id": ocorrencia.id, "titulo": ocorrencia.titulo},
        ocorrencia_id=ocorrencia.id,
    )
    return ocorrencia


@router.put("/{ocorrencia_id}", response_model=OcorrenciaRead)
async def atualizar(
    ocorrencia_id: int,
    data: OcorrenciaUpdate,
    service: Annotated[OcorrenciaService, Depends(_get_service)],
):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar",
        )
    try:
        ocorrencia = await service.atualizar(ocorrencia_id, update_data)
    except OcorrenciaNaoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TransicaoStatusInvalida as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    await _broadcast_event(
        EventType.OCORRENCIA_ATUALIZADA,
        {"ocorrencia_id": ocorrencia.id, "status": ocorrencia.status, "titulo": ocorrencia.titulo},
        ocorrencia_id=ocorrencia.id,
    )
    return ocorrencia


@router.delete("/{ocorrencia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover(
    ocorrencia_id: int,
    service: Annotated[OcorrenciaService, Depends(_get_service)],
):
    try:
        await service.remover(ocorrencia_id)
    except OcorrenciaNaoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    await _broadcast_event(
        EventType.OCORRENCIA_REMOVIDA,
        {"ocorrencia_id": ocorrencia_id},
        ocorrencia_id=ocorrencia_id,
    )
