"""Integration tests for Morador REST endpoints."""

from collections.abc import AsyncGenerator
from datetime import UTC
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from httpx import ASGITransport

from app.main import app
from app.routers.morador import _get_service
from app.services.morador import (
    MoradorComCPFJaExiste,
    MoradorComEmailJaExiste,
    MoradorNaoEncontrado,
)


@pytest.fixture
def mock_service() -> MagicMock:
    service = MagicMock()
    service.criar = AsyncMock()
    service.listar = AsyncMock()
    service.buscar = AsyncMock()
    service.listar_por_apartamento = AsyncMock()
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


def _make_morador(
    morador_id: int = 1,
    nome: str = "João Silva",
    cpf: str = "111.222.333-44",
) -> dict:
    from datetime import datetime

    obj = MagicMock()
    obj.id = morador_id
    obj.nome = nome
    obj.cpf = cpf
    obj.email = "joao@email.com"
    obj.telefone = "(11) 99999-0000"
    obj.tipo = "proprietario"
    obj.apartamento_id = 1
    obj.created_at = datetime.now(UTC)
    obj.updated_at = datetime.now(UTC)
    return obj


# ── GET /moradores ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_listar_retorna_lista(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    a, b = _make_morador(1, "João"), _make_morador(2, "Maria")
    mock_service.listar.return_value = [a, b]

    response = await client.get("/moradores/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nome"] == "João"
    assert data[1]["nome"] == "Maria"


@pytest.mark.asyncio
async def test_listar_retorna_vazia(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.listar.return_value = []

    response = await client.get("/moradores/")

    assert response.status_code == 200
    assert response.json() == []


# ── GET /moradores/{id} ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_obter_retorna_morador(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.buscar.return_value = _make_morador()

    response = await client.get("/moradores/1")

    assert response.status_code == 200
    assert response.json()["nome"] == "João Silva"


@pytest.mark.asyncio
async def test_obter_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.buscar.side_effect = MoradorNaoEncontrado("não encontrado")

    response = await client.get("/moradores/999")

    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


# ── POST /moradores ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_criar_retorna_201(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.criar.return_value = _make_morador()

    response = await client.post(
        "/moradores/",
        json={
            "nome": "João Silva",
            "cpf": "111.222.333-44",
            "email": "joao@email.com",
            "apartamento_id": 1,
        },
    )

    assert response.status_code == 201
    assert response.json()["nome"] == "João Silva"


@pytest.mark.asyncio
async def test_criar_422_quando_dados_invalidos(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.post("/moradores/", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_criar_409_quando_cpf_duplicado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.criar.side_effect = MoradorComCPFJaExiste("CPF já cadastrado")

    response = await client.post(
        "/moradores/",
        json={
            "nome": "Outro",
            "cpf": "111.222.333-44",
            "email": "outro@email.com",
            "apartamento_id": 1,
        },
    )

    assert response.status_code == 409
    assert "CPF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_criar_409_quando_email_duplicado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.criar.side_effect = MoradorComEmailJaExiste("Email já cadastrado")

    response = await client.post(
        "/moradores/",
        json={
            "nome": "Outro",
            "cpf": "999.999.999-99",
            "email": "joao@email.com",
            "apartamento_id": 1,
        },
    )

    assert response.status_code == 409
    assert "Email" in response.json()["detail"]


# ── PUT /moradores/{id} ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_atualizar_retorna_200(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.atualizar.return_value = _make_morador(nome="Nome Atualizado")

    response = await client.put("/moradores/1", json={"nome": "Nome Atualizado"})

    assert response.status_code == 200
    assert response.json()["nome"] == "Nome Atualizado"


@pytest.mark.asyncio
async def test_atualizar_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.atualizar.side_effect = MoradorNaoEncontrado("não encontrado")

    response = await client.put("/moradores/999", json={"nome": "Qualquer"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_409_quando_cpf_duplicado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.atualizar.side_effect = MoradorComCPFJaExiste("CPF já pertence a outro morador")

    response = await client.put(
        "/moradores/1",
        json={"cpf": "111.222.333-44"},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_atualizar_422_quando_cpf_invalido(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.put("/moradores/1", json={"cpf": "123"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_atualizar_400_quando_sem_campos(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.put("/moradores/1", json={})

    assert response.status_code == 400
    assert "Nenhum campo" in response.json()["detail"]


# ── DELETE /moradores/{id} ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_remover_retorna_204(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    response = await client.delete("/moradores/1")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_remover_404_quando_nao_encontrado(client: httpx.AsyncClient, override_deps: None, mock_service: MagicMock):
    mock_service.remover.side_effect = MoradorNaoEncontrado("não encontrado")

    response = await client.delete("/moradores/999")

    assert response.status_code == 404
