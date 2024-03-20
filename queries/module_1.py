import asyncio

from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

sqlite_url = "sqlite+aiosqlite:///basic_db.sqlite3"
engine = create_async_engine(url=sqlite_url, connect_args={"check_same_thread": False}, future=True)
async_session = AsyncSession(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(length=20), unique=True)
    name: Mapped[str] = mapped_column(String(length=60), nullable=True)
    surname: Mapped[str] = mapped_column(String(length=60), nullable=True)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы созданы")


async def create_user(username: str):
    async with async_session as session:
        user = User(username=username)
        session.add(user)
        await session.commit()


async def main():
    await init_models()
    await create_user(username='Vina Sky')


if __name__ == '__main__':
    asyncio.run(main())
