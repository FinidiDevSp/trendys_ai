"""Base protocol for notification adapters.

Every notification adapter must implement the Notifier protocol.
See CLAUDE.md §9 for conventions.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Notifier(Protocol):
    async def send(self, item: object, profile: object) -> bool:
        """Send a notification for a classified item to the given profile's channel."""
        ...

    def channel_type(self) -> str:
        """Return the identifier for this channel type (e.g., 'email', 'telegram')."""
        ...
