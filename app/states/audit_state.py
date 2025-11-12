import reflex as rx
import datetime
import uuid
from typing import TypedDict


class AuditEvent(TypedDict):
    id: str
    timestamp: str
    user: str
    action: str
    client_id: str
    client_name: str
    details: str


class AuditState(rx.State):
    """Manages the audit trail for client data changes."""

    audit_events: list[AuditEvent] = []
    search_query: str = ""

    @rx.var
    def filtered_audit_events(self) -> list[AuditEvent]:
        """Filters audit events based on the search query."""
        if not self.search_query:
            return sorted(self.audit_events, key=lambda e: e["timestamp"], reverse=True)
        query = self.search_query.lower()
        return sorted(
            [
                event
                for event in self.audit_events
                if query in event["user"].lower()
                or query in event["action"].lower()
                or query in event["client_name"].lower()
                or (query in event["details"].lower())
            ],
            key=lambda e: e["timestamp"],
            reverse=True,
        )

    @rx.event
    async def add_event(
        self, user: str, action: str, client_id: str, client_name: str, details: str
    ):
        """Adds a new event to the audit trail."""
        event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            user=user,
            action=action,
            client_id=client_id,
            client_name=client_name,
            details=details,
        )
        self.audit_events.append(event)