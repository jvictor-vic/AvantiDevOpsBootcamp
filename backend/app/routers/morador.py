from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.morador import MoradorRepository
from app.schemas.morador import MoradorCreate, MoradorRead, MoradorUpdate
from app.services.morador import (
    MoradorComCPFJaExiste,
    MoradorComEmailJaExiste,
    MoradorNaoEncontrado,
    MoradorService,
)

router = APIRouter(prefix="/moradores", tags=["moradores"])


async def _get_service(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> MoradorService:
    return MoradorService(MoradorRepository(session))


@router.get("/", response_model=list[MoradorRead])
async def listar_moradores(service: Annotated[MoradorService, Depends(_get_service)]):
    return await service.listar()


@router.get("/{morador_id}", response_model=MoradorRead)
async def obter_morador(
    morador_id: int,
    service: Annotated[MoradorService, Depends(_get_service)],
):
    try:
        return await service.buscar(morador_id)
    except MoradorNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=MoradorRead, status_code=status.HTTP_201_CREATED)
async def criar_morador(
    data: MoradorCreate,
    service: Annotated[MoradorService, Depends(_get_service)],
):
    try:
        return await service.criar(
            nome=data.nome,
            cpf=data.cpf,
            email=str(data.email),
            telefone=data.telefone,
            tipo=data.tipo,
            apartamento_id=data.apartamento_id,
        )
    except (MoradorComCPFJaExiste, MoradorComEmailJaExiste) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put("/{morador_id}", response_model=MoradorRead)
async def atualizar_morador(
    morador_id: int,
    data: MoradorUpdate,
    service: Annotated[MoradorService, Depends(_get_service)],
):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum campo para atualizar")
    try:
        return await service.atualizar(morador_id, update_data)
    except MoradorNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (MoradorComCPFJaExiste, MoradorComEmailJaExiste) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{morador_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_morador(
    morador_id: int,
    service: Annotated[MoradorService, Depends(_get_service)],
):
    try:
        await service.remover(morador_id)
    except MoradorNaoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
