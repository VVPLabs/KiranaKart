from sqlmodel import select
from db.models import User
from utils.hashing import generate_pass_hash
from auth.schemas import UserRegister
from fastapi import Depends
from db.session import get_session
from sqlmodel.ext.asyncio.session import AsyncSession


class AuthService:
    async def get_user_by_email(
        self, email: str, session: AsyncSession = Depends(get_session)
    ):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()

        return user

    async def get_user_by_username(
        self, username: str, session: AsyncSession = Depends(get_session)
    ):
        statement = select(User).where(User.username == username)

        result = await session.exec(statement)

        user = result.first()

        return user

    async def user_exists(
        self, email: str, session: AsyncSession = Depends(get_session)
    ):
        user = await self.get_user_by_email(email, session)

        return user is not None

    async def create_user(
        self, user_data: UserRegister, session: AsyncSession = Depends(get_session)
    ):
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)
        new_user.password_hash = generate_pass_hash(user_data_dict["password"])
        session.add(new_user)
        await session.commit()
        return new_user

    async def update_user(
        self, user: User, user_data: dict, session: AsyncSession = Depends(get_session)
    ):
        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        return user
