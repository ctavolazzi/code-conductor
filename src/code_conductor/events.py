from typing import Callable, Any
import logging

class Event:
    """
    Event class for work effort events.
    """
    def __init__(self, type: str, data: Any = None):
        """
        Initialize a new event.

        Args:
            type: Type of the event
            data: Data associated with the event
        """
        self.type = type
        self.data = data

class EventEmitter:
    """
    Simple event emitter for work effort events.
    """
    def __init__(self):
        """Initialize a new event emitter."""
        self.handlers = {}

    def on(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for an event type (alias for register_handler).

        Args:
            event_type: Type of the event
            handler: Function to call when event is emitted
        """
        self.register_handler(event_type, handler)

    def register(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for an event type (alias for register_handler).

        Args:
            event_type: Type of the event
            handler: Function to call when event is emitted
        """
        self.register_handler(event_type, handler)

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for an event type.

        Args:
            event_type: Type of the event
            handler: Function to call when event is emitted
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def emit(self, event: Event) -> None:
        """
        Emit an event, calling all registered handlers.

        Args:
            event: Event to emit
        """
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                handler(event)

    def emit_event(self, event_type: str, data: Any = None) -> None:
        """
        Create and emit an event of the specified type.

        This is a convenience method that creates an Event and calls emit().
        It is provided for backward compatibility with older code.

        Args:
            event_type: Type of the event to emit
            data: Data to include with the event
        """
        event = Event(event_type, data)
        self.emit(event)

class LoggingHandler:
    """
    Handler that logs events.
    """
    def __init__(self, logger=None):
        """
        Initialize a new logging handler.

        Args:
            logger: Logger to use, or None to use the default logger
        """
        self.logger = logger or logging.getLogger(__name__)

    def __call__(self, event: Event) -> None:
        """
        Handle an event by logging it.

        This makes the handler callable, which is needed for compatibility with tests.

        Args:
            event: Event to log
        """
        self.handle(event)

    def handle(self, event: Event) -> None:
        """
        Handle an event by logging it.

        Args:
            event: Event to log
        """
        self.logger.info(f"Event: {event.type}, Data: {event.data}")