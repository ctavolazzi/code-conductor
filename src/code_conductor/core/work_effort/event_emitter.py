from typing import Dict, Any, Callable, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    """Represents a work effort event."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.now()

class EventEmitter:
    """Handles work effort events."""

    def __init__(self):
        """Initialize the event emitter."""
        self.listeners: Dict[str, List[Callable[[Event], None]]] = {}

    def on(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Register an event listener.

        Args:
            event_type: The type of event to listen for.
            callback: The callback function to call when the event occurs.
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        self.listeners[event_type].append(callback)

    def off(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Remove an event listener.

        Args:
            event_type: The type of event to stop listening for.
            callback: The callback function to remove.
        """
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)

    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event.

        Args:
            event_type: The type of event to emit.
            data: The event data.
        """
        event = Event(type=event_type, data=data)

        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(event)

    def clear(self) -> None:
        """Clear all event listeners."""
        self.listeners.clear()