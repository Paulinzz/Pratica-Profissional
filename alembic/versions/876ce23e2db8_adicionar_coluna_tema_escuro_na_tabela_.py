"""Adicionar coluna tema_escuro na tabela User

Revision ID: 876ce23e2db8
Revises: 3ddcfea462c8
Create Date: 2025-11-20 21:51:51.303770

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "876ce23e2db8"
down_revision: Union[str, Sequence[str], None] = "3ddcfea462c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adicionar coluna tema_escuro na tabela user
    op.add_column(
        "user", sa.Column("tema_escuro", sa.Boolean(), nullable=True, default=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remover coluna tema_escuro da tabela user
    op.drop_column("user", "tema_escuro")
