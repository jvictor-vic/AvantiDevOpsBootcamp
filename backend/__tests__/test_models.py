"""Tests for SQLAlchemy ORM models — TDD approach."""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    Apartamento,
    Condominio,
    Morador,
    Ocorrencia,
    Rivalidade,
)


@pytest.mark.asyncio
async def test_create_condominio(async_session):
    """Deve criar um Condominio com campos obrigatórios."""
    cond = Condominio(nome="Condomínio das Flores", endereco="Rua das Flores, 123")
    async_session.add(cond)
    await async_session.commit()
    await async_session.refresh(cond)

    assert cond.id is not None
    assert cond.nome == "Condomínio das Flores"
    assert cond.endereco == "Rua das Flores, 123"


@pytest.mark.asyncio
async def test_create_apartamento(async_session):
    """Deve criar um Apartamento vinculado a um Condominio."""
    cond = Condominio(nome="Edifício Central", endereco="Av. Paulista, 1000")
    async_session.add(cond)
    await async_session.flush()

    apt = Apartamento(numero="101", bloco="A", condominio_id=cond.id)
    async_session.add(apt)
    await async_session.commit()
    await async_session.refresh(apt)

    assert apt.id is not None
    assert apt.numero == "101"
    assert apt.bloco == "A"
    assert apt.condominio_id == cond.id


@pytest.mark.asyncio
async def test_create_morador(async_session):
    """Deve criar um Morador vinculado a um Apartamento."""
    cond = Condominio(nome="Residencial Park", endereco="Rua Verde, 500")
    async_session.add(cond)
    await async_session.flush()

    apt = Apartamento(numero="42", condominio_id=cond.id)
    async_session.add(apt)
    await async_session.flush()

    mor = Morador(
        nome="João Silva",
        cpf="123.456.789-00",
        email="joao@email.com",
        apartamento_id=apt.id,
    )
    async_session.add(mor)
    await async_session.commit()
    await async_session.refresh(mor)

    assert mor.id is not None
    assert mor.nome == "João Silva"
    assert mor.email == "joao@email.com"
    assert mor.tipo == "proprietario"  # default


@pytest.mark.asyncio
async def test_create_ocorrencia(async_session):
    """Deve criar uma Ocorrencia vinculada a um Apartamento."""
    cond = Condominio(nome="Cond Tower", endereco="Rua X, 100")
    async_session.add(cond)
    await async_session.flush()

    apt = Apartamento(numero="201", condominio_id=cond.id)
    async_session.add(apt)
    await async_session.flush()

    oco = Ocorrencia(
        titulo="Festa alta madrugada",
        descricao="Música alta após meia-noite",
        categoria="barulho",
        gravidade="alta",
        apartamento_id=apt.id,
    )
    async_session.add(oco)
    await async_session.commit()
    await async_session.refresh(oco)

    assert oco.id is not None
    assert oco.titulo == "Festa alta madrugada"
    assert oco.categoria == "barulho"
    assert oco.gravidade == "alta"
    assert oco.status == "aberta"  # default


@pytest.mark.asyncio
async def test_create_rivalidade(async_session):
    """Deve criar uma Rivalidade N:N entre dois Apartamentos."""
    cond = Condominio(nome="Cond Park", endereco="Rua Y, 200")
    async_session.add(cond)
    await async_session.flush()

    apt_a = Apartamento(numero="1", condominio_id=cond.id)
    apt_b = Apartamento(numero="2", condominio_id=cond.id)
    async_session.add_all([apt_a, apt_b])
    await async_session.flush()

    riv = Rivalidade(
        apartamento_a_id=apt_a.id,
        apartamento_b_id=apt_b.id,
        motivo="Vaga de garagem",
        nivel="intenso",
    )
    async_session.add(riv)
    await async_session.commit()
    await async_session.refresh(riv)

    assert riv.id is not None
    assert riv.motivo == "Vaga de garagem"
    assert riv.nivel == "intenso"
    assert riv.status == "ativa"


@pytest.mark.asyncio
async def test_condominio_apartamentos_relationship(async_session):
    """Condominio.apartamentos deve retornar lista de Apartamentos."""
    cond = Condominio(nome="Cond Rel", endereco="Rua Z, 300")
    async_session.add(cond)
    await async_session.flush()

    apt1 = Apartamento(numero="A1", condominio_id=cond.id)
    apt2 = Apartamento(numero="A2", condominio_id=cond.id)
    async_session.add_all([apt1, apt2])
    await async_session.commit()

    result = await async_session.execute(
        select(Condominio).where(Condominio.id == cond.id).options(selectinload(Condominio.apartamentos))
    )
    cond_db = result.scalar_one()
    assert len(cond_db.apartamentos) == 2
    assert {a.numero for a in cond_db.apartamentos} == {"A1", "A2"}


@pytest.mark.asyncio
async def test_apartamento_moradores_relationship(async_session):
    """Apartamento.moradores deve retornar lista de Moradores."""
    cond = Condominio(nome="Cond Fam", endereco="Rua W, 400")
    async_session.add(cond)
    await async_session.flush()

    apt = Apartamento(numero="10", condominio_id=cond.id)
    async_session.add(apt)
    await async_session.flush()

    m1 = Morador(nome="Ana", cpf="111.222.333-44", email="ana@email.com", apartamento_id=apt.id)
    m2 = Morador(nome="Beto", cpf="555.666.777-88", email="beto@email.com", apartamento_id=apt.id)
    async_session.add_all([m1, m2])
    await async_session.commit()

    result = await async_session.execute(
        select(Apartamento).where(Apartamento.id == apt.id).options(selectinload(Apartamento.moradores))
    )
    apt_db = result.scalar_one()
    assert len(apt_db.moradores) == 2
    assert {m.nome for m in apt_db.moradores} == {"Ana", "Beto"}


def test_unique_constraint_apartamento():
    """Verifica que existe constraint única para numero+bloco+torre+condominio_id no modelo."""
    from sqlalchemy import inspect
    from app.models import Apartamento
    insp = inspect(Apartamento.__table__)
    unique_constraints = [c for c in insp.constraints if hasattr(c, 'columns') and c.__class__.__name__ == 'UniqueConstraint']
    assert any(
        set(c.columns.keys()) == {"numero", "bloco", "torre", "condominio_id"}
        for c in unique_constraints
    )


def test_unique_constraint_rivalidade():
    """Verifica que existe constraint única para par (apartamento_a, apartamento_b) no modelo."""
    from sqlalchemy import inspect
    from app.models import Rivalidade
    insp = inspect(Rivalidade.__table__)
    unique_constraints = [c for c in insp.constraints if hasattr(c, 'columns') and c.__class__.__name__ == 'UniqueConstraint']
    assert any(
        set(c.columns.keys()) == {"apartamento_a_id", "apartamento_b_id"}
        for c in unique_constraints
    )
