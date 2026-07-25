"""message node parent variant unique constraint

Revision ID: 63f19e69a72d
Revises: b2f1a9c4d7e3
Create Date: 2026-07-24 21:42:05.551680

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "63f19e69a72d"
down_revision: Union[str, Sequence[str], None] = "b2f1a9c4d7e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The race this constraint guards against predates the guard, so a real DB
    # can already hold duplicate (parent_id, variant_index) siblings from it.
    # Renumber every non-root row by insertion order (id ASC) within its
    # parent group before the constraint lands, so the batch table-rebuild's
    # copy step never trips on pre-existing duplicates. This is data-preserving
    # (no rows dropped, unlike a DELETE-based cleanup) and a no-op for already-
    # well-formed rows: variant_index is normally count-of-earlier-siblings at
    # insert time, i.e. exactly this same rank.
    op.execute(
        """
        UPDATE message_nodes
        SET variant_index = (
            SELECT COUNT(*)
            FROM message_nodes AS earlier
            WHERE earlier.parent_id = message_nodes.parent_id
              AND earlier.id < message_nodes.id
        )
        WHERE parent_id IS NOT NULL
        """
    )

    # DB-level backstop for _persist_assistant_reply's count-derived
    # variant_index: two concurrent regenerate/stream inserts under the same
    # parent can otherwise land duplicate (parent_id, variant_index) rows.
    with op.batch_alter_table("message_nodes", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_message_node_parent_variant", ["parent_id", "variant_index"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("message_nodes", schema=None) as batch_op:
        batch_op.drop_constraint("uq_message_node_parent_variant", type_="unique")
