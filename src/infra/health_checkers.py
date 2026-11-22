import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from src.domain.enums import SystemComponent
from src.domain.interfaces.health_checker import ComponentHealthStatus

logger = logging.getLogger(__name__)


class PostgresHealthChecker:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def check(self) -> ComponentHealthStatus:
        """Checking the PostgreSQL status."""
        try:
            async with asyncio.timeout(2):
                async with self._engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
        except OSError, SQLAlchemyError:
            logger.warning("PostgreSQL health check failed", exc_info=True)
            return ComponentHealthStatus(
                component_name=SystemComponent.POSTGRES,
                is_healthy=False,
                error_msg="PostgreSQL health check failed",
            )

        return ComponentHealthStatus(
            component_name=SystemComponent.POSTGRES, is_healthy=True
        )
