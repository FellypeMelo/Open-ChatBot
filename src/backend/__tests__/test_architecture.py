"""Architecture fitness tests.

Lightweight guards that pin the Clean Architecture dependency rule: the pure
domain layer must not depend on the persistence (db) layer. These fail loudly
if a future edit re-couples the domain to SQLAlchemy models.
"""

import inspect

from src.backend.core.engine import state_transitions


def test_state_transitions_domain_does_not_import_db_layer():
    source = inspect.getsource(state_transitions)
    assert "src.backend.db" not in source, (
        "state_transitions is domain logic and must depend on core.ports, "
        "not the persistence layer"
    )
