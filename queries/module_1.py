import asyncio

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

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    username: Mapped[str] = mapped_column(String(length=20), unique=True)
    name: Mapped[str] = mapped_column(String(length=60), nullable=True)
    surname: Mapped[str] = mapped_column(String(length=60), nullable=True)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы созданы\n")


async def create_user(username: str):
    async with async_session as session:
        user = User(username=username)
        await session.commit()
        session.add(user)


async def get_all_users():
    async with async_session as session:
        users = await session.execute(
            select(User))  # <sqlalchemy.engine.result.ChunkedIteratorResult object at 0x7fe0009a6cc0>
        users_scalars = users.scalars().all()
        print(users_scalars)

        for usr in users_scalars:
            print(f"id: {usr.id}, username: {usr.username}")
        return users_scalars


async def get_user_by_id(user_id: int):
    async with async_session as session:
        user = await session.get(User, user_id)
        print(f"\nGot user with id {user.id}: username: {user.username}")

        return user


async def get_filtered_users():
    async with async_session as session:
        # filtered_users = await session.execute(select(User).filter(User.id == 4))
        filtered_user = await session.execute(select(User).filter(User.id == 4))
        filtered_users = await session.execute(select(User).filter(User.username.contains('a')))

        print(f'User filtered by id:')
        for user in filtered_user.first():
            print(f"    Username of user with id 4: {user.username}")

        # for user in filtered_users.all():  # AttributeError: id. Нужно использовать scalars()
        #     print(f"user: {user.id}, username: {user.username}")

        print(f'Users filtered by letter in username:')
        for user in filtered_users.scalars():
            print(f"    id: {user.id}, username: {user.username}")


async def update_user_by_id(user_id: int):
    async with async_session as session:
        user = await session.get(User, user_id)
        user.username = 'Charity Crawford'
        print(f'\nUser with id {user_id} has been modified')
        await session.commit()


async def delete_user_by_id(user_id: int):
    async with async_session as session:
        user = await session.get(User, user_id)

        print(f'User for delete: {user.username}')

        await session.delete(user)
        print(f'User with id {user_id} has been deleted')
        await session.commit()


async def main():
    await init_models()
    await create_user(username='Vina Sky')
    await get_all_users()
    await get_user_by_id(3)
    await get_filtered_users()
    await update_user_by_id(1)
    await delete_user_by_id(3)


if __name__ == '__main__':
    asyncio.run(main())
