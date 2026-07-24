"""Integration tests for Rivalidade REST endpoints."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from httpx import ASGITransport

from app.main import app
from app.routers.rivalidade import _get_service
from app.services.rivalidade import (
    NivelInvalido,
    RivalidadeJaExiste,
    RivalidadeNaoEncontrada,
)


@pytest.fixture
def mock_service() -> MagicMock:
    service = MagicMock()
    service.criar = AsyncMock()
    service.listar = AsyncMock()
    service.listar_por_apartamento = AsyncMock()
    service.top_rivalidades = AsyncMock()
    service.buscar = AsyncMock()
    service.escalar = AsyncMock()
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
        "apartamento_a_id": 101,
        "apartamento_b_id": 102,
        "motivo": "Barulho",
        "nivel": "moderado",
        "status": "ativa",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    vals.update(kw)
    return MagicMock(**vals)


# ── GET /rivalidades ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_listar_retorna_lista(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    a, b = _make(id=1), _make(id=2, apartamento_a_id=201)
    mock_service.listar.return_value = [a, b]

    response = await client.get("/rivalidades/")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_listar_retorna_vazia(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.listar.return_value = []

    response = await client.get("/rivalidades/")

    assert response.status_code == 200
    assert response.json() == []


# ── GET /rivalidades/por-apartamento/{id} ─────────────────────────────


@pytest.mark.asyncio
async def test_por_apartamento_retorna_lista(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.listar_por_apartamento.return_value = [_make(), _make(id=2)]

    response = await client.get("/rivalidades/por-apartamento/101")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_por_apartamento_retorna_vazia(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.listar_por_apartamento.return_value = []

    response = await client.get("/rivalidades/por-apartamento/999")

    assert response.status_code == 200
    assert response.json() == []


# ── GET /rivalidades/top ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_top_retorna_lista(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.top_rivalidades.return_value = [_make(), _make(id=2, nivel="belico")]

    response = await client.get("/rivalidades/top")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_top_com_limite(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.top_rivalidades.return_value = [_make(), _make(id=2)]

    response = await client.get("/rivalidades/top?limite=5")

    assert response.status_code == 200


# ── GET /rivalidades/{id} ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_obter_retorna_rivalidade(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.buscar.return_value = _make()

    response = await client.get("/rivalidades/1")

    assert response.status_code == 200
    assert response.json()["motivo"] == "Barulho"


@pytest.mark.asyncio
async def test_obter_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.buscar.side_effect = RivalidadeNaoEncontrada("não encontrada")

    response = await client.get("/rivalidades/999")

    assert response.status_code == 404


# ── POST /rivalidades ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_criar_retorna_201(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.criar.return_value = _make()

    response = await client.post(
        "/rivalidades/",
        json={
            "apartamento_a_id": 101,
            "apartamento_b_id": 102,
            "motivo": "Barulho",
            "nivel": "moderado",
        },
    )

    assert response.status_code == 201
    assert response.json()["motivo"] == "Barulho"


@pytest.mark.asyncio
async def test_criar_422_quando_dados_invalidos(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.post("/rivalidades/", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_criar_409_quando_rivalidade_ja_existe(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.criar.side_effect = RivalidadeJaExiste("já existe")

    response = await client.post(
        "/rivalidades/",
        json={
            "apartamento_a_id": 101,
            "apartamento_b_id": 102,
            "nivel": "moderado",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_criar_409_quando_nivel_invalido(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.criar.side_effect = NivelInvalido("nivel inválido")

    response = await client.post(
        "/rivalidades/",
        json={
            "apartamento_a_id": 101,
            "apartamento_b_id": 102,
            "nivel": "moderado",
        },
    )

    assert response.status_code == 409


# ── POST /rivalidades/{id}/escalar ─────────────────────────────────────


@pytest.mark.asyncio
async def test_escalar_retorna_200(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.escalar.return_value = _make(nivel="intenso")

    response = await client.post("/rivalidades/1/escalar")

    assert response.status_code == 200
    assert response.json()["nivel"] == "intenso"


@pytest.mark.asyncio
async def test_escalar_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.escalar.side_effect = RivalidadeNaoEncontrada("não encontrada")

    response = await client.post("/rivalidades/999/escalar")

    assert response.status_code == 404


# ── PUT /rivalidades/{id} ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_atualizar_retorna_200(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.atualizar.return_value = _make(motivo="Novo motivo")

    response = await client.put("/rivalidades/1", json={"motivo": "Novo motivo"})

    assert response.status_code == 200
    assert response.json()["motivo"] == "Novo motivo"


@pytest.mark.asyncio
async def test_atualizar_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.atualizar.side_effect = RivalidadeNaoEncontrada("não encontrada")

    response = await client.put("/rivalidades/999", json={"motivo": "X"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_422_quando_nivel_invalido(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    # schema validation catches invalid nivel before service
    response = await client.put("/rivalidades/1", json={"nivel": "invalido"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_atualizar_400_sem_campos(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.put("/rivalidades/1", json={})

    assert response.status_code == 400


# ── DELETE /rivalidades/{id} ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_remover_retorna_204(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.delete("/rivalidades/1")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_remover_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.remover.side_effect = RivalidadeNaoEncontrada("não encontrada")

    response = await client.delete("/rivalidades/999")

    assert response.status_code == 404
