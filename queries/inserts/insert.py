import asyncio

from sqlalchemy import String, Integer, insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

sqlite_url = "sqlite+aiosqlite:///inserts.sqlite3"
engine = create_async_engine(
    url=sqlite_url, connect_args={"check_same_thread": False}, future=True
)
async_session = AsyncSession(bind=engine)


class Base(DeclarativeBase):
    pass


class Worker(Base):
    __tablename__ = "workers"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    username: Mapped[str] = mapped_column(String(), unique=True)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created\n")


async def insert_data():
    async with async_session as session:
        stmt = insert(Worker).values(
            [
                {"username": "1"},
                {"username": "2"},
            ]
        )
        await session.execute(stmt)
        await session.commit()


async def main():
    await create_tables()
    await insert_data()


if __name__ == "__main__":
    asyncio.run(main())
