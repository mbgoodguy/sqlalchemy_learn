import asyncio

from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, create_session

sqlite_url = "sqlite+aiosqlite:///basic_db.sqlite3"
engine = create_async_engine(url=sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
async_session = SessionLocal()


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


async def create_user(name: str, username: str):
    async with async_session as session:  # Используйте вызов асинхронного сеанса
        user = User(name=name, username=username)
        session.add(user)
        await session.commit()  # Асинхронный вызов метода commit()
        print(f"User has been created. User's id: {user.id}")
        print(user.id)


if __name__ == '__main__':
    asyncio.run(init_models())
    asyncio.run(create_user(name='Megan', username='Fox'))
