from typing import Optional

import sqlalchemy.orm as so
import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

sqlite_url = "sqlite:///db.sqlite3"
engine = create_engine(url=sqlite_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(engine)


# helper for getting DB object using for interacting with DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(
    DeclarativeBase
):  # allows to convert regular classes into sql alchemy models
    pass


# SQLAlchemy table model
class User(Base):
    __tablename__ = "users"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(String(64), index=True, unique=True)
    email: so.Mapped[Optional[str]] = so.mapped_column(
        String(120), index=True, unique=True, nullable=True
    )
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(
        String(128), nullable=True
    )
    about_me: so.Mapped[Optional[str]] = so.mapped_column(String(140), nullable=True)


#  Чтобы в запрос не заполнять все поля, сделаем в модели таблицы необязательными через nullable=True
# а в модели Pydantic для полей которые необязательные к заполнению, укажем Optional[str] = None


# Pydantic model
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    password_hash: Optional[str] = None
    about_me: Optional[str] = None


try:
    Base.metadata.create_all(engine)  # create all models in DB
    print("База данных и таблица созданы")
except Exception as e:
    print(e)

#  uvicorn sync_sqlite3_app:app --reload  - запуск приложения
app = FastAPI()


@app.post("/create_user")
def create_user(user: UserBase, db: Session = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(
        db_user
    )  # put the extra info on the user object which will be id because it'sgenerated when save to the DB

    return db_user


@app.get("/users")
def get_user(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users}


if __name__ == "__main__":
    uvicorn.run("sync_sqlite3_app:app", port=8001, reload=True)  # http://127.0.0.1:8001
