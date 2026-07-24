"""Unit tests for RivalidadeService."""

from datetime import UTC
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.rivalidade import RivalidadeRepository
from app.services.rivalidade import (
    NivelInvalido,
    RivalidadeJaExiste,
    RivalidadeNaoEncontrada,
    RivalidadeService,
)


@pytest.fixture
def repo() -> MagicMock:
    return MagicMock(spec=RivalidadeRepository)


@pytest.fixture
def service(repo: MagicMock) -> RivalidadeService:
    return RivalidadeService(repo)


def _make_rivalidade(**kw: dict) -> MagicMock:
    from datetime import datetime

    vals: dict = {
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


class TestCriar:
    async def test_cria_rivalidade(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_between = AsyncMock(return_value=None)
        repo.create = AsyncMock(return_value=MagicMock(id=1))
        result = await service.criar(101, 102, motivo="Barulho", nivel="moderado")
        assert result.id == 1
        repo.create.assert_awaited_once()

    async def test_rejeita_apartamentos_iguais(self, service: RivalidadeService, repo: MagicMock) -> None:
        with pytest.raises(RivalidadeJaExiste, match="Não é possível criar rivalidade consigo mesmo"):
            await service.criar(101, 101)
        repo.create.assert_not_called()

    async def test_rejeita_rivalidade_ja_existente(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_between = AsyncMock(return_value=MagicMock())
        with pytest.raises(RivalidadeJaExiste):
            await service.criar(101, 102)
        repo.create.assert_not_called()

    async def test_rejeita_nivel_invalido(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_between = AsyncMock(return_value=None)
        with pytest.raises(NivelInvalido):
            await service.criar(101, 102, nivel="invalido")
        repo.create.assert_not_called()


class TestListar:
    async def test_lista_todos(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_all = AsyncMock(return_value=[MagicMock(), MagicMock()])
        result = await service.listar()
        assert len(result) == 2

    async def test_lista_vazio(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_all = AsyncMock(return_value=[])
        assert await service.listar() == []


class TestBuscar:
    async def test_retorna_quando_encontrado(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=_make_rivalidade())
        result = await service.buscar(1)
        assert result.id == 1

    async def test_lanca_excecao_quando_nao_encontrado(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(RivalidadeNaoEncontrada):
            await service.buscar(999)


class TestListarPorApartamento:
    async def test_retorna_rivalidades_do_apto(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_by_apartamento = AsyncMock(return_value=[MagicMock(), MagicMock()])
        result = await service.listar_por_apartamento(101)
        assert len(result) == 2

    async def test_retorna_vazio_quando_nenhuma(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_by_apartamento = AsyncMock(return_value=[])
        assert await service.listar_por_apartamento(999) == []


class TestTopRivalidades:
    async def test_retorna_top_rivalidades(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.top_rivalidades = AsyncMock(return_value=[MagicMock(), MagicMock()])
        result = await service.top_rivalidades(limite=5)
        assert len(result) == 2
        repo.top_rivalidades.assert_awaited_once_with(5)


class TestEscalar:
    async def test_escala_nivel(self, service: RivalidadeService, repo: MagicMock) -> None:
        rivalidade = _make_rivalidade(nivel="moderado")
        repo.get_by_id = AsyncMock(return_value=rivalidade)
        repo.update = AsyncMock(return_value=_make_rivalidade(nivel="intenso"))
        result = await service.escalar(1)
        assert result.nivel == "intenso"

    async def test_nao_escala_quando_ja_no_maximo(self, service: RivalidadeService, repo: MagicMock) -> None:
        rivalidade = _make_rivalidade(nivel="belico")
        repo.get_by_id = AsyncMock(return_value=rivalidade)
        result = await service.escalar(1)
        assert result.nivel == "belico"
        repo.update.assert_not_awaited()


class TestAtualizar:
    async def test_atualiza_campos(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=_make_rivalidade())
        repo.update = AsyncMock(return_value=_make_rivalidade(motivo="Novo motivo"))
        result = await service.atualizar(1, {"motivo": "Novo motivo"})
        assert result.motivo == "Novo motivo"

    async def test_rejeita_nivel_invalido(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=_make_rivalidade())
        with pytest.raises(NivelInvalido):
            await service.atualizar(1, {"nivel": "invalido"})
        repo.update.assert_not_awaited()

    async def test_lanca_excecao_quando_nao_encontrado(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(RivalidadeNaoEncontrada):
            await service.atualizar(999, {"motivo": "X"})
        repo.update.assert_not_awaited()


class TestRemover:
    async def test_remove(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.delete = AsyncMock(return_value=True)
        await service.remover(1)
        repo.delete.assert_awaited_once_with(1)

    async def test_lanca_excecao_quando_nao_encontrado(self, service: RivalidadeService, repo: MagicMock) -> None:
        repo.delete = AsyncMock(return_value=False)
        with pytest.raises(RivalidadeNaoEncontrada):
            await service.remover(999)
