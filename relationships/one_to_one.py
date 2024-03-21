import asyncio

from sqlalchemy import String, ForeignKey, Integer, CheckConstraint
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

DB_URL = "sqlite+aiosqlite:///one_to_one.sqlite3"

engine = create_async_engine(
    url=DB_URL, connect_args={"check_same_thread": False}, future=True
)
async_session = AsyncSession(bind=engine)


class Base(DeclarativeBase):
    pass


class Citizen(Base):
    __tablename__ = "citizens"

    # nulalble - чтобы не заполнять все поля каждый раз
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=60))
    first_name: Mapped[str] = mapped_column(String(length=60), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(length=60), nullable=True)
    last_name: Mapped[str] = mapped_column(String(length=60), nullable=True)

    passport_id: Mapped[int] = relationship(
        "Passport", backref="citizen", uselist=False
    )


class Passport(Base):
    __tablename__ = "passports"

    id: Mapped[int] = mapped_column(primary_key=True)
    serial: Mapped[int] = mapped_column(
        Integer(), CheckConstraint("LENGTH(serial) = 4")
    )
    number: Mapped[int] = mapped_column(
        Integer(), CheckConstraint("LENGTH(number) = 6")
    )

    citizen_id: Mapped[int] = mapped_column(
        Integer(),
        ForeignKey(
            "citizens.id",
        ),
    )


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print(f"Tables created")


async def add_citizen(name: str, **args):
    async with async_session as session:
        session.add(Citizen(name=name))
        await session.commit()


async def add_passport(serial: int, number: int, citizen_id: int):
    async with async_session as session:
        try:
            session.add(Passport(serial=serial, number=number, citizen_id=citizen_id))
            print(f"Passport has been added")
            await session.commit()
        except Exception as e:
            print(e)


async def main():
    await init_models()
    await add_passport(serial=3425, number=128246, citizen_id=1)


if __name__ == "__main__":
    asyncio.run(main())
