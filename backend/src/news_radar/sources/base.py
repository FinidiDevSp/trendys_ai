"""Base protocol for source connectors.

Every source connector must implement the SourceConnector protocol.
See CLAUDE.md §8 for conventions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class SourceConnector(Protocol):
    async def fetch_items(self, since: datetime | None = None) -> list:
        """Fetch new items from the source since the given timestamp."""
        ...

    def source_type(self) -> str:
        """Return the identifier for this source type (e.g., 'rss', 'youtube')."""
        ...
