#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Work Effort event system.

This module provides an event system for handling work effort events.
"""

import logging
import time
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from threading import Thread, Event as ThreadEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WorkEfforts.Events")

@dataclass
class Event:
    """
    Represents an event in the system.

    Attributes:
        type: The type of event
        data: The data associated with the event
    """
    type: str
    data: Any = None

class EventEmitter:
    """
    Emits events to registered handlers.
    """

    def __init__(self):
        """Initialize the event emitter."""
        self.handlers: Dict[str, List[Callable]] = {}
        self.running = False
        self.stop_event = ThreadEvent()
        self.event_thread = None

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for an event type.

        Args:
            event_type: The type of event to handle
            handler: The function to call when the event occurs
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")

    def emit_event(self, event_type: str, data: Any = None) -> None:
        """
        Emit an event to all registered handlers.

        Args:
            event_type: The type of event
            data: The data associated with the event
        """
        event = Event(type=event_type, data=data)

        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {str(e)}")

        logger.info(f"Emitted event: {event_type}")

    def start_event_loop(self, check_interval: float = 1.0, check_function: Optional[Callable] = None) -> None:
        """
        Start the event loop in a separate thread.

        Args:
            check_interval: The interval between checks in seconds
            check_function: A function to call on each iteration of the event loop
        """
        if self.running:
            logger.warning("Event loop is already running")
            return

        self.running = True
        self.stop_event.clear()

        def run_loop():
            logger.info("Started event loop")

            while self.running and not self.stop_event.is_set():
                try:
                    # Run the check function if provided
                    if check_function:
                        check_function()

                    # Sleep for the check interval
                    time.sleep(check_interval)
                except Exception as e:
                    logger.error(f"Error in event loop: {str(e)}")

            logger.info("Stopped event loop")

        self.event_thread = Thread(target=run_loop, daemon=True)
        self.event_thread.start()

    def stop_event_loop(self) -> None:
        """Stop the event loop."""
        if not self.running:
            logger.warning("Event loop is not running")
            return

        self.running = False
        self.stop_event.set()

        if self.event_thread:
            self.event_thread.join(timeout=2.0)
            self.event_thread = None

        logger.info("Stopped event loop")


# Handler types

class EventHandler:
    """Base class for event handlers."""

    def __init__(self, name: str):
        """
        Initialize the event handler.

        Args:
            name: The name of the handler
        """
        self.name = name

    def __call__(self, event: Event) -> None:
        """
        Handle an event.

        Args:
            event: The event to handle
        """
        raise NotImplementedError("Subclasses must implement this method")


class LoggingHandler(EventHandler):
    """Logs events to the console."""

    def __init__(self, name: str = "LoggingHandler"):
        """Initialize the logging handler."""
        super().__init__(name)

    def __call__(self, event: Event) -> None:
        """
        Log an event.

        Args:
            event: The event to log
        """
        logger.info(f"Event: {event.type}, Data: {event.data}")


class FileSystemWatchHandler(EventHandler):
    """Handles file system change events."""

    def __init__(self, project_dir: str, name: str = "FileSystemWatchHandler"):
        """
        Initialize the file system watch handler.

        Args:
            project_dir: The project directory to watch
            name: The name of the handler
        """
        super().__init__(name)
        self.project_dir = project_dir

    def __call__(self, event: Event) -> None:
        """
        Handle a file system event.

        Args:
            event: The event to handle
        """
        if event.type == "file_changed":
            logger.info(f"File changed: {event.data}")
        elif event.type == "file_created":
            logger.info(f"File created: {event.data}")
        elif event.type == "file_deleted":
            logger.info(f"File deleted: {event.data}")
        else:
            logger.info(f"Unknown file system event: {event.type}")


# Factory function to create an event emitter
def create_event_emitter() -> EventEmitter:
    """
    Create an event emitter.

    Returns:
        A new event emitter
    """
    return EventEmitter()


# Standalone functions for working with events

def register_handler(emitter: EventEmitter, event_type: str, handler: Callable) -> None:
    """
    Register a handler with an emitter.

    Args:
        emitter: The event emitter
        event_type: The type of event to handle
        handler: The function to call when the event occurs
    """
    emitter.register_handler(event_type, handler)

def emit_event(emitter: EventEmitter, event_type: str, data: Any = None) -> None:
    """
    Emit an event through an emitter.

    Args:
        emitter: The event emitter
        event_type: The type of event
        data: The data associated with the event
    """
    emitter.emit_event(event_type, data)

def start_event_loop(emitter: EventEmitter, check_interval: float = 1.0, check_function: Optional[Callable] = None) -> None:
    """
    Start the event loop on an emitter.

    Args:
        emitter: The event emitter
        check_interval: The interval between checks in seconds
        check_function: A function to call on each iteration of the event loop
    """
    emitter.start_event_loop(check_interval, check_function)

def stop_event_loop(emitter: EventEmitter) -> None:
    """
    Stop the event loop on an emitter.

    Args:
        emitter: The event emitter
    """
    emitter.stop_event_loop()