"""Unit tests for OcorrenciaRepository."""

from datetime import UTC
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ocorrencia import Ocorrencia
from app.repositories.ocorrencia import OcorrenciaRepository


@pytest.fixture
def session() -> MagicMock:
    mock = AsyncMock(spec=AsyncSession)
    mock.add = MagicMock()
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()
    mock.delete = AsyncMock()
    mock.execute = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock()
    result_mock.scalars = MagicMock()
    result_mock.scalars.return_value.all = MagicMock()
    mock.execute.return_value = result_mock
    return mock


@pytest.fixture
def repo(session: MagicMock) -> OcorrenciaRepository:
    return OcorrenciaRepository(session)


def _make(**kw: dict) -> MagicMock:
    from datetime import datetime

    vals: dict = {
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
    m = MagicMock(spec=Ocorrencia)
    for k, v in vals.items():
        setattr(m, k, v)
    return m


class TestCreate:
    async def test_creates(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        o = _make()
        result = await repo.create(o)
        session.add.assert_called_once_with(o)
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(o)
        assert result == o


class TestGetById:
    async def test_returns_when_found(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        session.execute.return_value.scalar_one_or_none.return_value = _make()
        result = await repo.get_by_id(1)
        assert result is not None
        assert result.id == 1

    async def test_returns_none_when_not_found(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        session.execute.return_value.scalar_one_or_none.return_value = None
        assert await repo.get_by_id(999) is None


class TestGetAll:
    @pytest.mark.parametrize("filtros", [
        {},
        {"categoria": "barulho"},
        {"status": "aberta"},
        {"gravidade": "alta"},
        {"apartamento_id": 1},
    ])
    async def test_aplica_filtros(self, repo: OcorrenciaRepository, session: MagicMock, filtros: dict) -> None:
        session.execute.return_value.scalars.return_value.all.return_value = []
        result = await repo.get_all(**filtros)
        assert result == []

    async def test_retorna_lista(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        a, b = _make(id=1), _make(id=2, titulo="Outro")
        session.execute.return_value.scalars.return_value.all.return_value = [a, b]
        result = await repo.get_all()
        assert len(result) == 2


class TestListRecentes:
    async def test_retorna_recentes(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        session.execute.return_value.scalars.return_value.all.return_value = [_make()]
        result = await repo.list_recentes()
        assert len(result) == 1


class TestUpdate:
    async def test_updates(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        o = _make()
        repo.get_by_id = AsyncMock(return_value=o)
        result = await repo.update(1, {"status": "resolvida"})
        assert o.status == "resolvida"  # type: ignore[attr-defined]
        session.commit.assert_awaited_once()
        assert result == o

    async def test_returns_none_when_not_found(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.update(999, {}) is None
        session.commit.assert_not_called()


class TestDelete:
    async def test_deletes(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=_make())
        assert await repo.delete(1) is True
        session.delete.assert_awaited_once()
        session.commit.assert_awaited_once()

    async def test_returns_false_when_not_found(self, repo: OcorrenciaRepository, session: MagicMock) -> None:
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.delete(999) is False
        session.delete.assert_not_called()
