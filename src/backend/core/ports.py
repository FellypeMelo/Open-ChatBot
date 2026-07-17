"""Domain ports (structural interfaces).

The pure domain layer (e.g. state_transitions) must not depend on the
SQLAlchemy persistence models -- that would invert the Clean Architecture
dependency rule (high-level policy depending on a low-level detail). Instead it
depends on these Protocols. The ORM models structurally satisfy them, so the
concrete persistence type is injected at the edges without the domain ever
importing it.
"""

from typing import Any, Dict, Optional, Protocol


class AgentStateLike(Protocol):
    """The mutable agent-state surface the narrative-action transitions read and
    write. `AgentState` (the ORM model) satisfies this structurally."""

    location: Optional[str]
    clothes: Optional[str]
    stats: Optional[Dict[str, Any]]
