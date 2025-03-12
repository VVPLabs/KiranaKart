from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from user.schemas import UserResponse, UserUpdate
from auth.dependencies import RoleChecker, AccessTokenBearer
from datetime import datetime, timezone
from user.services import UserService
from auth.services import AuthService
from sqlmodel.ext.asyncio.session import AsyncSession
from db.session import get_session


User_router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()
auth_service = AuthService()
role_checker = RoleChecker()
access_token_bearer = AccessTokenBearer()


def remove_timezone(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


@User_router.get("/all", response_model=List[UserResponse])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    users_data = await user_service.get_all_users(session)
    return users_data


@User_router.get("/self", response_model=UserResponse)
async def get_active_user(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    username = token_details["username"]
    user = await auth_service.get_user_by_username(username, session)
    return user


@User_router.put("/deactivate")
async def deactivate_user(
    token_details=Depends(access_token_bearer),
    session: AsyncSession = Depends(get_session),
):
    username = token_details["username"]
    user = await auth_service.get_user_by_username(username, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already deactivated"
        )
    deactivate_data = UserUpdate(
            is_active=False, deleted_at=remove_timezone(datetime.now(timezone.utc))
        )
    deactivated_user = await user_service.update_user(
            user.user_id, deactivate_data, session
        )
    if not deactivated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER NOT FOUND"
        )
    await session.commit()
    return {"message": "Account deactivated successfully"}


@User_router.put("/reactivate")
async def reactivate_user(
    token_details=Depends(access_token_bearer),
    session: AsyncSession = Depends(get_session),
):
    username = token_details["username"]
    user = await auth_service.get_user_by_username(username, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active"
        )

    reactivate_data = UserUpdate(is_active=True, deleted_at=None)
    reactivated_user = await user_service.update_user(
        user.user_id, reactivate_data, session
    )

    if not reactivated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER NOT FOUND"
        )
    await session.commit()
    return {"message": "Your account is now active"}

@User_router.delete("/delete")
async def delete_user(session :AsyncSession= Depends(get_session), token_details= Depends(access_token_bearer)):
    username = token_details["username"]
    is_admin= token_details["is_admin"]
    user = await auth_service.get_user_by_username(username, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot delete their own account")
    await user_service.delete_user(username, user.user_id, session)
    await session.commit()

    return {"message": "User account deleted permanently"}


@User_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
    _: bool = Depends(role_checker),
):
    return await user_service.get_user(user_id, session)


@User_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id,
    user_update_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):

    updated_user = await user_service.update_user(user_id, user_update_data, session)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER NOT FOUND"
        )
    await session.commit()
    return updated_user
