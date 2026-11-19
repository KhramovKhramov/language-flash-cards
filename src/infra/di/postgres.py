from collections.abc import AsyncIterable, AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import Settings


class PostgresProvider(Provider):
    """PostgreSQL DI provider."""

    scope = Scope.APP

    @provide
    async def get_engine(
        self, settings: Settings
    ) -> AsyncIterator[AsyncEngine]:
        db_url = URL.create(
            drivername="postgresql+asyncpg",
            username=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=int(settings.DB_PORT) if settings.DB_PORT else None,
            database=settings.DB_NAME,
        )
        engine = create_async_engine(db_url, echo=settings.DEBUG)
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide
    def get_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session
            await session.commit()
