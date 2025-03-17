#!/usr/bin/env python3
"""
This module provides a basic event system for the code conductor.
It enables components to communicate through events.
"""

import logging
from typing import Dict, List, Callable, Any

class Event:
    """
    Class representing an event in the system.
    """
    def __init__(self, event_type=None, data=None, type=None):
        """
        Initialize an event with a type and optional data.

        Args:
            event_type (str): The type of the event
            data (dict, optional): Data associated with the event
            type (str, optional): Alternative name for event_type for backward compatibility
        """
        # For backward compatibility
        if type is not None and event_type is None:
            event_type = type

        self.event_type = event_type
        self.type = event_type  # For backward compatibility
        self.data = data or {}

    def __str__(self):
        """
        Return a string representation of the event.

        Returns:
            str: String representation of the event
        """
        return f"Event({self.event_type}, {self.data})"

class EventEmitter:
    """
    Manages event listeners and emits events to registered handlers.
    """
    def __init__(self):
        """
        Initialize an empty dictionary of event listeners.
        """
        self.listeners = {}

    def register_handler(self, event_type, callback):
        """
        Register a callback for a specific event type.

        Args:
            event_type (str): The type of event to listen for
            callback (callable): The function to call when event occurs
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def emit_event(self, event):
        """
        Emit an event to all registered handlers for its type.

        Args:
            event (Event): The event to emit
        """
        if event.event_type in self.listeners:
            for callback in self.listeners[event.event_type]:
                callback(event)

    def remove_handler(self, event_type, callback):
        """
        Remove a specific handler for an event type.

        Args:
            event_type (str): The type of event
            callback (callable): The callback to remove
        """
        if event_type in self.listeners:
            if callback in self.listeners[event_type]:
                self.listeners[event_type].remove(callback)

    def remove_all_handlers(self, event_type=None):
        """
        Remove all handlers for a specific event type or all handlers if no type specified.

        Args:
            event_type (str, optional): The type of event. If None, removes all handlers.
        """
        if event_type:
            if event_type in self.listeners:
                self.listeners[event_type] = []
        else:
            self.listeners = {}

    # Compatibility with existing on/emit methods
    def on(self, event_type, callback):
        """
        Alias for register_handler.
        """
        self.register_handler(event_type, callback)

    def emit(self, event_type, data=None):
        """
        Create and emit an event with the given type and data.

        Args:
            event_type (str): The type of event to emit
            data (dict, optional): The data to include with the event
        """
        event = Event(event_type, data)
        self.emit_event(event)

class LoggingHandler:
    """
    Handles logging events to the console or a file.
    """
    def __init__(self, log_file=None):
        """
        Initialize a logging handler.

        Args:
            log_file (str, optional): Path to log file, if None logs to console
        """
        self.log_file = log_file

    def handle_event(self, event):
        """
        Handle an event by logging it.

        Args:
            event (Event): The event to handle
        """
        log_message = f"[{event.event_type}] {event.data}"
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(log_message + "\n")
        else:
            print(log_message)

    def register_with_emitter(self, emitter, event_types=None):
        """
        Register this handler with an emitter for specific event types.

        Args:
            emitter (EventEmitter): The emitter to register with
            event_types (list, optional): List of event types to handle, if None handles all
        """
        if event_types:
            for event_type in event_types:
                emitter.register_handler(event_type, self.handle_event)
        else:
            # No types specified, so register a general handler
            def general_handler(event):
                self.handle_event(event)

            # Store reference to avoid garbage collection
            self.general_handler = general_handler
            emitter.register_handler("*", general_handler)

# Re-export common classes needed by tests
try:
    from src.code_conductor.events import EventEmitter, Event, LoggingHandler
except ImportError:
    # If the import fails, define the classes here for compatibility
    from typing import Callable, Dict, List, Any, Optional, Union
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