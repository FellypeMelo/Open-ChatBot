"""character dynamic_persona flag (EPIC Phase 3 static/dynamic toggle)

Revision ID: b2f1a9c4d7e3
Revises: f6926d3f5da7
Create Date: 2026-07-17

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2f1a9c4d7e3"
down_revision: Union[str, Sequence[str], None] = "f6926d3f5da7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add characters.dynamic_persona (default True). Guarded so it is
    idempotent with the init_db ALTER-compat path (a transitioning DB may
    already carry the column before it is upgraded through Alembic)."""
    from sqlalchemy import inspect

    bind = op.get_bind()
    existing = {c["name"] for c in inspect(bind).get_columns("characters")}
    if "dynamic_persona" not in existing:
        op.add_column(
            "characters",
            sa.Column("dynamic_persona", sa.Boolean(), server_default=sa.text("1")),
        )


def downgrade() -> None:
    with op.batch_alter_table("characters") as batch:
        batch.drop_column("dynamic_persona")
