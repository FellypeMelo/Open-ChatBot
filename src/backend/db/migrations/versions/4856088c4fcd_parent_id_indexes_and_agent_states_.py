"""parent_id indexes and agent_states character_id not null

Revision ID: 4856088c4fcd
Revises: 886d9e36d0c1
Create Date: 2026-07-17 11:53:48.258856

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4856088c4fcd"
down_revision: Union[str, Sequence[str], None] = "886d9e36d0c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # B3: index message_nodes.parent_id (hot predicate) + the subtree-walk and
    # per-chat active-history composites.
    op.create_index("ix_message_nodes_parent_id", "message_nodes", ["parent_id"])
    op.create_index(
        "ix_message_nodes_parent_active",
        "message_nodes",
        ["parent_id", "is_active"],
    )
    op.create_index(
        "ix_message_nodes_chat_active_ts",
        "message_nodes",
        ["chat_id", "is_active", "timestamp"],
    )

    # B4: agent_states.character_id -> NOT NULL. Drop any orphaned state (no
    # character) first -- it is unreachable anyway -- so the constraint can hold.
    op.execute("DELETE FROM agent_states WHERE character_id IS NULL")
    with op.batch_alter_table("agent_states", schema=None) as batch_op:
        batch_op.alter_column(
            "character_id", existing_type=sa.Integer(), nullable=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("agent_states", schema=None) as batch_op:
        batch_op.alter_column("character_id", existing_type=sa.Integer(), nullable=True)
    op.drop_index("ix_message_nodes_chat_active_ts", table_name="message_nodes")
    op.drop_index("ix_message_nodes_parent_active", table_name="message_nodes")
    op.drop_index("ix_message_nodes_parent_id", table_name="message_nodes")
