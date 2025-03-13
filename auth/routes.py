from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from auth.schemas import (
    UserRegister,
    UserLogin,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from auth.services import AuthService
from sqlmodel.ext.asyncio.session import AsyncSession
from db.session import get_session
from utils.hashing import verify_pass, generate_pass_hash
from utils.tokens import (
    create_url_safe_token,
    decode_url_safe_token,
    create_access_token,
    verify_token,
)
from celery_tasks import send_password_reset_email, send_verfification_email
from auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from db.redis import add_jti_to_blocklist

Auth_router = APIRouter(prefix="/auth", tags=["Auth"])
user_service = AuthService()


@Auth_router.post("/register")
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists",
        )

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})
    background_tasks.add_task(send_verfification_email, email, token)

    return {
        "message": "Account created successfully. Please check your email for verification.",
        "user": new_user,
    }


@Auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    if token_data is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await user_service.update_user(user, {"is_verified": True}, session)

        return {"message": "Account Verified Successfully", "user": user}
    return JSONResponse(
        content={
            "message": "Error occured during verification ",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@Auth_router.post("/login")
async def login(login_data: UserLogin, session: AsyncSession = Depends(get_session)):
    username: str = login_data.username
    password: str = login_data.password

    user = await user_service.get_user_by_username(username, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    password_valid = verify_pass(password, user.password_hash)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        {
            "username": user.username,
            "user_id": str(user.user_id),
            "role": user.role,
        }
    )
    refresh_token = create_access_token(
        {"username": user.username, "user_id": str(user.user_id)},
        refresh=True,
        expires_delta=timedelta(days=2),
    )

    response = JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "user_details": {
                "username": username,
                "user_id": str(user.user_id),
                "mail": user.email,
            },
        }
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return response


@Auth_router.post("/logout")
async def logout(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(str(jti))

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "LOGGED OUT SUCCESSFULLY"}
    )


@Auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["expires_delta"]
    if expiry_timestamp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing expiry timestamp in token{token_details}"

    )
    if expiry_timestamp > datetime.now(timezone.utc):
        new_access_token = create_access_token(user_data={
            "username": token_details["username"],
            "user_id": str(token_details["user_id"]),
            "role": token_details["role"],
        })
        return {"access_token ": new_access_token}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID OR EXPIRED TOKEN "
    )


@Auth_router.post("/password_reset_request")
async def password_reset_request(
    email_data: PasswordResetRequestModel, background_tasks: BackgroundTasks
):
    email = email_data.email
    token = create_url_safe_token({"email": email})

    background_tasks.add_task(send_password_reset_email, email, token)


@Auth_router.post("password_reset_confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_password

    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_200_OK, detail="passwords don't match"
        )

    token_data = decode_url_safe_token(token)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        passwd_hash = generate_pass_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)

        return {"message": "Password update successfully", "user": user}
    return JSONResponse(
        content={
            "message": "Error occured during password reset ",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
