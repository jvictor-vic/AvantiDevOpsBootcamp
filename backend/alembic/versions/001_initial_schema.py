"""initial schema — create all 5 domain tables

Revision ID: 001
Revises:
Create Date: 2026-05-31 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- condominios ---
    op.create_table(
        "condominios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("endereco", sa.String(300), nullable=False),
        sa.Column("cnpj", sa.String(18), nullable=True, unique=True),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- apartamentos ---
    op.create_table(
        "apartamentos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("numero", sa.String(10), nullable=False),
        sa.Column("bloco", sa.String(10), nullable=True),
        sa.Column("torre", sa.String(50), nullable=True),
        sa.Column("area", sa.Float(), nullable=True),
        sa.Column("condominio_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["condominio_id"],
            ["condominios.id"],
            name="fk_apartamento_condominio",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "numero",
            "bloco",
            "torre",
            "condominio_id",
            name="uq_apartamento_identificacao",
        ),
    )
    op.create_index(
        "ix_apartamento_condominio", "apartamentos", ["condominio_id"]
    )

    # --- moradores ---
    op.create_table(
        "moradores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("cpf", sa.String(14), nullable=False, unique=True),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column(
            "tipo", sa.String(20), nullable=False, server_default="proprietario"
        ),
        sa.Column("apartamento_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["apartamento_id"],
            ["apartamentos.id"],
            name="fk_morador_apartamento",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_morador_apartamento", "moradores", ["apartamento_id"]
    )

    # --- ocorrencias ---
    op.create_table(
        "ocorrencias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("categoria", sa.String(50), nullable=False),
        sa.Column(
            "gravidade", sa.String(20), nullable=False, server_default="media"
        ),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="aberta"
        ),
        sa.Column("apartamento_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["apartamento_id"],
            ["apartamentos.id"],
            name="fk_ocorrencia_apartamento",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ocorrencia_categoria", "ocorrencias", ["categoria"]
    )
    op.create_index(
        "ix_ocorrencia_status", "ocorrencias", ["status"]
    )
    op.create_index(
        "ix_ocorrencia_apartamento", "ocorrencias", ["apartamento_id"]
    )
    op.create_index(
        "ix_ocorrencia_created_at", "ocorrencias", ["created_at"]
    )

    # --- rivalidades ---
    op.create_table(
        "rivalidades",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("apartamento_a_id", sa.Integer(), nullable=False),
        sa.Column("apartamento_b_id", sa.Integer(), nullable=False),
        sa.Column("motivo", sa.String(200), nullable=True),
        sa.Column(
            "nivel", sa.String(20), nullable=False, server_default="moderado"
        ),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="ativa"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["apartamento_a_id"],
            ["apartamentos.id"],
            name="fk_rivalidade_apartamento_a",
        ),
        sa.ForeignKeyConstraint(
            ["apartamento_b_id"],
            ["apartamentos.id"],
            name="fk_rivalidade_apartamento_b",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "apartamento_a_id",
            "apartamento_b_id",
            name="uq_rivalidade_apartamentos",
        ),
    )
    op.create_index(
        "ix_rivalidade_apartamento_a",
        "rivalidades",
        ["apartamento_a_id"],
    )
    op.create_index(
        "ix_rivalidade_apartamento_b",
        "rivalidades",
        ["apartamento_b_id"],
    )


def downgrade() -> None:
    op.drop_table("rivalidades")
    op.drop_table("ocorrencias")
    op.drop_table("moradores")
    op.drop_table("apartamentos")
    op.drop_table("condominios")
