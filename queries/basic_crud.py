import asyncio
from typing import Any, Union

from sqlalchemy import String, select
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


def check_is_falsy(obj: Any):
    return bool(obj)


async def user_exists(session: AsyncSession, user_id: int):
    user = await session.get(User, user_id)

    return bool(user)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created\n")


async def create_user(username: str, user_id: Union[int, None] = None):
    async with async_session as session:
        if user_id is not None and await user_exists(session=session, user_id=user_id):
            print("User with this ID already exists. Cannot create a new user with the same ID.")
        else:
            user = User(username=username)
            session.add(user)
            await session.commit()
            print("User created\n")


async def get_all_users():
    async with async_session as session:
        users = await session.execute(select(User))  # sqlalchemy.engine.result.ChunkedIteratorResult object
        users_scalars = users.scalars().all()
        # print(users_scalars)

        for usr in users_scalars:
            print(f"id: {usr.id}, username: {usr.username}")
        return users_scalars


async def get_user_by_id(user_id: int):
    async with async_session as session:
        user = await session.get(User, user_id)

        if await user_exists(session=session, user_id=user_id):
            print(f"\nGot user with id {user.id}: username: {user.username}\n")
        else:
            print(f"User with id {user_id} doesn't exists\n")


async def get_filtered_users(user_id: int, letter: Union[str | None] = None):
    async with async_session as session:
        # filtered_users = await session.execute(select(User).filter(User.id == 4))

        # filtered_users_scalars = filtered_users.scalars()

        if await user_exists(session=session, user_id=user_id):
            filtered_user = await session.get(User, user_id)
            print(f"Username of user with id 4: {filtered_user.username}")
        else:
            print(f"User with id {user_id} doesn't exist")

        if await user_exists(session=session, user_id=user_id) and letter is not None:
            filtered_users = await session.execute(select(User).filter(User.username.contains(letter)))
            print(f'Users with letter {letter} in username:')
            for user in filtered_users.scalars():
                print(f"    id: {user.id}, username: {user.username}")
        else:
            print(f"There are no filtered users \n")

        # for user in filtered_users.all():  # AttributeError: id. Нужно использовать scalars()
        #     print(f"user: {user.id}, username: {user.username}")


async def update_user_by_id(user_id: int, username: str):
    async with async_session as session:
        user = await session.get(User, user_id)
        if await user_exists(session=session, user_id=user_id):
            if username:
                user.username = username
                print(f'\nUser with id {user_id} has been modified')
                await session.commit()
        else:
            print(f"\nUser with id {user_id} doesn't exist")


async def delete_user_by_id(user_id: int):
    async with async_session as session:
        user = await session.get(User, user_id)

        if await user_exists(session=session, user_id=user_id):
            await session.delete(user)
            print(f'\tUser with id {user_id} has been deleted')
            await session.commit()
        else:
            print(f"\nUser with id {user_id} doesn't exist")


async def main():
    await init_models()
    # await create_user(username='q')  # ok
    # await get_all_users()  # ok
    # await get_user_by_id(3)  # ok
    # await get_filtered_users(3)  # ok
    # await update_user_by_id(user_id=7, username='Lily Larimar')
    await delete_user_by_id(user_id=7)


if __name__ == '__main__':
    asyncio.run(main())
