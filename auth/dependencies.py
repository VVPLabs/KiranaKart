from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from utils.tokens import verify_token
from db.redis import token_in_blocklist
from typing import List
from db.models import User, UserRole
from db.session import get_session
from auth.services import AuthService


user_service = AuthService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    def token_valid(self, token: str) -> bool:

        try:
            token_data = verify_token(token)
            return token_data is not None
        except Exception:
            return False

    def verify_token_data(self, token_data: dict) -> None:

        raise NotImplementedError("please override in child class")

    async def __call__(self, request: Request):
        creds = await super().__call__(request)

        if creds is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No credentials provided",
            )
        token = creds.credentials

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "Error": "THIS TOKEN IS INVALID OR HAS BEEN REVOKED",
                    "Resolution": "PLEASE GET A NEW TOKEN",
                },
            )

        token_data = verify_token(token).model_dump()


        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "THIS TOKEN IS INVALID OR HAS BEEN REVOKED",
                    "resolution": "PLEASE GET A NEW TOKEN",
                },
            )
        self.verify_token_data(token_data)

        return token_data


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="PROVIDE A VALID ACCESS TOKEN",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="PROVIDE A VALID REFRESH TOKEN",
            )


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    username = token_details.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="username missing in token")

    user = await user_service.get_user_by_username(username, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Account not verified",
                    "resolution": "Please check your email for verification ",
                },
            )
        if not any(role in self.allowed_roles for role in current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="YOU ARE NOT PERMITTED TO PERFORM THIS ACTION",
            )
        return current_user