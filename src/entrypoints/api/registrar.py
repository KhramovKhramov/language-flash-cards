from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.core.config import Settings
from src.entrypoints.api.openapi import TAGS_METADATA
from src.entrypoints.api.router import api_router
from src.infra.di.health_checkers import HealthCheckersProvider
from src.infra.di.postgres import PostgresProvider
from src.infra.di.settings import SettingsProvider
from src.infra.di.use_cases import UseCasesProvider


def create_app(settings: Settings) -> FastAPI:
    """FastAPI app registration."""

    container = make_async_container(
        SettingsProvider(settings=settings),
        PostgresProvider(),
        HealthCheckersProvider(),
        UseCasesProvider(),
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await container.close()

    app = FastAPI(
        lifespan=lifespan,
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        docs_url=settings.FASTAPI_DOCS_URL,
        redoc_url=settings.FASTAPI_REDOC_URL,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        openapi_tags=TAGS_METADATA,
    )

    setup_dishka(container, app)

    # API-routers registration
    app.include_router(api_router)

    return app
