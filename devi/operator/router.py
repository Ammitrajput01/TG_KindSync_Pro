# -*- coding: utf-8 -*-
"""
Devi Operator O(1) Command Dispatcher & High-Speed Router
Provides microsecond command dispatching across 300+ Telegram bot commands.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

from typing import Callable, Coroutine, Any, Dict, List, Optional
import logging

logger = logging.getLogger("DEVI.CommandRouter")

class CommandRouter:
    """O(1) Hash-Map Command Dispatcher with Aliasing & Category Introspection."""
    
    def __init__(self):
        self._handlers: Dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}
        self._descriptions: Dict[str, str] = {}
        self._categories: Dict[str, List[str]] = {}

    def register(self, commands: List[str], handler: Callable, description: str = "", category: str = "general"):
        """Registers a handler for one or multiple command aliases in O(1) table."""
        for cmd in commands:
            clean = cmd.lower().lstrip("/")
            self._handlers[clean] = handler
            if description:
                self._descriptions[clean] = description
            if category not in self._categories:
                self._categories[category] = []
            if clean not in self._categories[category]:
                self._categories[category].append(clean)

    def dispatch(self, cmd_name: str) -> Optional[Callable]:
        """Dispatches command in O(1) time without sequential if/elif evaluation."""
        clean = cmd_name.lower().lstrip("/")
        return self._handlers.get(clean)

    def has_command(self, cmd_name: str) -> bool:
        """Checks command existence in O(1) time."""
        clean = cmd_name.lower().lstrip("/")
        return clean in self._handlers

    @property
    def total_commands(self) -> int:
        return len(self._handlers)

    def get_category_commands(self, category: str) -> List[str]:
        return self._categories.get(category, [])
