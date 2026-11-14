# -*- coding: utf-8 -*-
"""
Devi Operator Domain-Driven Command Handlers Master Registry
Initializes and aggregates all O(1) command routers across domains.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

from devi.operator.router import CommandRouter
from devi.operator.handlers.navigation import register_navigation_handlers
from devi.operator.handlers.clinical import register_clinical_handlers
from devi.operator.handlers.indexer import register_indexer_handlers
from devi.operator.handlers.account import register_account_handlers
from devi.operator.handlers.admin import register_admin_handlers

def build_master_router() -> CommandRouter:
    """Builds and compiles the master O(1) command routing table."""
    router = CommandRouter()
    register_navigation_handlers(router)
    register_clinical_handlers(router)
    register_indexer_handlers(router)
    register_account_handlers(router)
    register_admin_handlers(router)
    return router
