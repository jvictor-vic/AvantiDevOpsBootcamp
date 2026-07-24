"""Unit tests for OcorrenciaService."""

from datetime import UTC
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.ocorrencia import OcorrenciaRepository
from app.services.ocorrencia import (
    OcorrenciaNaoEncontrada,
    OcorrenciaService,
    TransicaoStatusInvalida,
)


@pytest.fixture
def repo() -> MagicMock:
    return MagicMock(spec=OcorrenciaRepository)


@pytest.fixture
def service(repo: MagicMock) -> OcorrenciaService:
    return OcorrenciaService(repo)


def _make_ocorrencia(**kw: dict) -> MagicMock:
    from datetime import datetime

    vals: dict = {
        "id": 1,
        "titulo": "Barulho",
        "descricao": "Música alta",
        "categoria": "barulho",
        "gravidade": "media",
        "status": "aberta",
        "apartamento_id": 1,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    vals.update(kw)
    return MagicMock(**vals)


class TestCriar:
    async def test_cria_ocorrencia(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.create = AsyncMock(return_value=MagicMock(id=1))
        result = await service.criar(
            titulo="Barulho",
            descricao="Música alta após 22h",
            categoria="barulho",
            apartamento_id=1,
        )
        assert result.id == 1
        repo.create.assert_awaited_once()


class TestListar:
    async def test_lista_com_filtros(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.get_all = AsyncMock(return_value=[MagicMock(), MagicMock()])
        result = await service.listar(categoria="barulho", status="aberta")
        assert len(result) == 2
        repo.get_all.assert_awaited_once_with("barulho", "aberta", None, None)

    async def test_lista_vazio(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.get_all = AsyncMock(return_value=[])
        assert await service.listar() == []


class TestBuscar:
    async def test_retorna_quando_encontrado(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=_make_ocorrencia())
        result = await service.buscar(1)
        assert result.id == 1

    async def test_lanca_excecao_quando_nao_encontrado(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(OcorrenciaNaoEncontrada):
            await service.buscar(999)


class TestListarRecentes:
    async def test_retorna_recentes(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.list_recentes = AsyncMock(return_value=[MagicMock()])
        result = await service.listar_recentes()
        assert len(result) == 1


class TestAtualizarStatus:
    async def test_transicao_valida(self, service: OcorrenciaService, repo: MagicMock) -> None:
        ocorrencia = _make_ocorrencia(status="aberta")
        repo.get_by_id = AsyncMock(return_value=ocorrencia)
        repo.update = AsyncMock(return_value=_make_ocorrencia(status="investigando"))

        result = await service.atualizar_status(1, "investigando")

        assert result.status == "investigando"

    async def test_transicao_invalida(self, service: OcorrenciaService, repo: MagicMock) -> None:
        ocorrencia = _make_ocorrencia(status="arquivada")
        repo.get_by_id = AsyncMock(return_value=ocorrencia)

        with pytest.raises(TransicaoStatusInvalida):
            await service.atualizar_status(1, "aberta")

    @pytest.mark.parametrize("de,para,valido", [
        ("aberta", "investigando", True),
        ("aberta", "resolvida", False),
        ("aberta", "arquivada", True),
        ("investigando", "resolvida", True),
        ("investigando", "aberta", True),
        ("resolvida", "arquivada", True),
        ("resolvida", "aberta", False),
        ("arquivada", "aberta", False),
    ])
    async def test_todas_transicoes(
        self, service: OcorrenciaService, repo: MagicMock,
        de: str, para: str, valido: bool,
    ) -> None:
        repo.get_by_id = AsyncMock(return_value=_make_ocorrencia(status=de))
        if valido:
            repo.update = AsyncMock(return_value=_make_ocorrencia(status=para))
            result = await service.atualizar_status(1, para)
            assert result.status == para
        else:
            with pytest.raises(TransicaoStatusInvalida):
                await service.atualizar_status(1, para)


class TestAtualizar:
    async def test_atualiza_campos(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=_make_ocorrencia())
        repo.update = AsyncMock(return_value=_make_ocorrencia(titulo="Novo"))
        result = await service.atualizar(1, {"titulo": "Novo"})
        assert result.titulo == "Novo"

    async def test_lanca_excecao_quando_nao_encontrado(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(OcorrenciaNaoEncontrada):
            await service.atualizar(999, {"titulo": "X"})


class TestRemover:
    async def test_remove(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.delete = AsyncMock(return_value=True)
        await service.remover(1)
        repo.delete.assert_awaited_once_with(1)

    async def test_lanca_excecao_quando_nao_encontrado(self, service: OcorrenciaService, repo: MagicMock) -> None:
        repo.delete = AsyncMock(return_value=False)
        with pytest.raises(OcorrenciaNaoEncontrada):
            await service.remover(999)
