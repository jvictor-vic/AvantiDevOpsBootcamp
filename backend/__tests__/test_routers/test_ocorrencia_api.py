"""Integration tests for Ocorrencia REST endpoints."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from httpx import ASGITransport

from app.main import app
from app.routers.ocorrencia import _get_service
from app.services.ocorrencia import (
    OcorrenciaNaoEncontrada,
    TransicaoStatusInvalida,
)


@pytest.fixture
def mock_service() -> MagicMock:
    service = MagicMock()
    service.criar = AsyncMock()
    service.listar = AsyncMock()
    service.listar_recentes = AsyncMock()
    service.buscar = AsyncMock()
    service.atualizar = AsyncMock()
    service.remover = AsyncMock()
    return service


@pytest.fixture
def override_deps(mock_service: MagicMock) -> AsyncGenerator[None]:
    async def _override() -> MagicMock:
        return mock_service

    app.dependency_overrides[_get_service] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def _make(**kw: dict) -> MagicMock:
    vals = {
        "id": 1,
        "titulo": "Barulho noturno",
        "descricao": "Música alta após 22h",
        "categoria": "barulho",
        "gravidade": "media",
        "status": "aberta",
        "apartamento_id": 1,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    vals.update(kw)
    m = MagicMock(**vals)
    return m


# ── GET /ocorrencias ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_listar_retorna_lista(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    a, b = _make(id=1), _make(id=2, titulo="Outro")
    mock_service.listar.return_value = [a, b]

    response = await client.get("/ocorrencias/")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_listar_com_filtros(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.listar.return_value = []

    response = await client.get("/ocorrencias/?categoria=barulho&status=aberta&gravidade=media&apartamento_id=1")

    assert response.status_code == 200
    assert response.json() == []
    mock_service.listar.assert_awaited_once_with("barulho", "aberta", "media", 1)


# ── GET /ocorrencias/recentes ────────────────────────────────────────


@pytest.mark.asyncio
async def test_recentes_retorna_lista(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.listar_recentes.return_value = [_make()]

    response = await client.get("/ocorrencias/recentes")

    assert response.status_code == 200
    assert len(response.json()) == 1


# ── GET /ocorrencias/{id} ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_obter_retorna_ocorrencia(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.buscar.return_value = _make()

    response = await client.get("/ocorrencias/1")

    assert response.status_code == 200
    assert response.json()["titulo"] == "Barulho noturno"


@pytest.mark.asyncio
async def test_obter_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.buscar.side_effect = OcorrenciaNaoEncontrada("não encontrada")

    response = await client.get("/ocorrencias/999")

    assert response.status_code == 404


# ── POST /ocorrencias ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_criar_retorna_201(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.criar.return_value = _make()

    response = await client.post(
        "/ocorrencias/",
        json={
            "titulo": "Barulho noturno",
            "descricao": "Música alta após 22h",
            "categoria": "barulho",
            "apartamento_id": 1,
        },
    )

    assert response.status_code == 201
    assert response.json()["titulo"] == "Barulho noturno"


@pytest.mark.asyncio
async def test_criar_422_quando_dados_invalidos(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.post("/ocorrencias/", json={})

    assert response.status_code == 422


# ── PUT /ocorrencias/{id} ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_atualizar_retorna_200(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.atualizar.return_value = _make(titulo="Novo Título")

    response = await client.put("/ocorrencias/1", json={"titulo": "Novo Título"})

    assert response.status_code == 200
    assert response.json()["titulo"] == "Novo Título"


@pytest.mark.asyncio
async def test_atualizar_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.atualizar.side_effect = OcorrenciaNaoEncontrada("não encontrada")

    response = await client.put("/ocorrencias/999", json={"titulo": "X"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_409_transicao_invalida(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.atualizar.side_effect = TransicaoStatusInvalida("Transição inválida")

    response = await client.put("/ocorrencias/1", json={"status": "aberta"})

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_atualizar_400_sem_campos(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.put("/ocorrencias/1", json={})

    assert response.status_code == 400


# ── DELETE /ocorrencias/{id} ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_remover_retorna_204(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.delete("/ocorrencias/1")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_remover_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.remover.side_effect = OcorrenciaNaoEncontrada("não encontrada")

    response = await client.delete("/ocorrencias/999")

    assert response.status_code == 404
