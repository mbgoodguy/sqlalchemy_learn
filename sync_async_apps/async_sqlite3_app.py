# for async work with db need pip install aiosqlite

from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)  # important difference from sync app

sqlite_url = "sqlite+aiosqlite:///async_db.sqlite3"
engine = create_async_engine(url=sqlite_url, connect_args={"check_same_thread": False})
SessionLocal = async_sessionmaker(engine)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # should not be create_all()
        print("Base.metadata.create_all has been completed")
        # используем run_sync т.к хотим запускать это асинхронно


# async helper for getting DB object using for interactingwith DB
async def get_db():
    await init_models()
    db = SessionLocal()
    try:
        yield db
        print("DB has been yielded")
    finally:
        await db.close()  # закрываем тоже асинхронно
        print("DB has been closed")


class Base(DeclarativeBase):  # allows to convert regular classesinto sql alchemy models
    pass


# SQLAlchemy table model
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    email: Mapped[Optional[str]] = mapped_column(
        String(120), index=True, unique=True, nullable=True
    )
    password_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    about_me: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)


#  Чтобы в запрос не заполнять все поля, сделаем в модели таблицы необязательными через nullable=True
# а в модели Pydantic для полей которые необязательные к заполнению, укажем Optional[str] = None
# Mapped - для указаня желаемого типа данных в столбце
# mapped_column - для указания доп.информации, ограничений столбца, например index=True, unique=True


# Pydantic model
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    password_hash: Optional[str] = None
    about_me: Optional[str] = None


#  uvicorn async_sqlite3_app:app --reload  - запуск приложения
app = FastAPI()


@app.post("/create_user")
async def create_user(user: UserBase, db: AsyncSession = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    await db.commit()
    await db.refresh(
        db_user
    )  # put the extra info on the user object which will be id because it'sgenerated when save to the DB

    return db_user


@app.get("/users")
async def get_user(db: AsyncSession = Depends(get_db)):
    # users = db.query(User).all()
    res = await db.execute(select(User))
    users = res.scalars().all()
    return {"users": users}


if __name__ == "__main__":
    uvicorn.run("async_sqlite3_app:app", port=8001, reload=True)  # http://127.0.0.1:8001
