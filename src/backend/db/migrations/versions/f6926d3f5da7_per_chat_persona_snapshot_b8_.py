"""per-chat persona snapshot (B8 independent storylines)

Revision ID: f6926d3f5da7
Revises: 4856088c4fcd
Create Date: 2026-07-17 12:00:23.450644

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f6926d3f5da7"
down_revision: Union[str, Sequence[str], None] = "4856088c4fcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # B8: per-chat persona snapshot. Guard each add so this is idempotent with
    # the init_db ALTER-compat path (a transitioning DB may already carry the
    # columns before it is upgraded through Alembic).
    from sqlalchemy import inspect

    bind = op.get_bind()
    existing = {c["name"] for c in inspect(bind).get_columns("chats")}

    if "location" not in existing:
        op.add_column(
            "chats", sa.Column("location", sa.String(), server_default="Living Room")
        )
    if "mood" not in existing:
        op.add_column("chats", sa.Column("mood", sa.String(), server_default="Neutral"))
    if "clothes" not in existing:
        op.add_column(
            "chats", sa.Column("clothes", sa.String(), server_default="Casual")
        )
    if "stats" not in existing:
        op.add_column("chats", sa.Column("stats", sa.JSON()))
        # Copy each character's current global persona into all its existing
        # chats so no storyline loses accumulated relationship/mood on the split.
        op.execute(
            "UPDATE chats SET "
            "location = COALESCE((SELECT location FROM agent_states s WHERE s.character_id = chats.character_id), 'Living Room'), "
            "mood = COALESCE((SELECT mood FROM agent_states s WHERE s.character_id = chats.character_id), 'Neutral'), "
            "clothes = COALESCE((SELECT clothes FROM agent_states s WHERE s.character_id = chats.character_id), 'Casual'), "
            "stats = (SELECT stats FROM agent_states s WHERE s.character_id = chats.character_id)"
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("chats", "stats")
    op.drop_column("chats", "clothes")
    op.drop_column("chats", "mood")
    op.drop_column("chats", "location")
