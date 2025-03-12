import jwt
import uuid
from datetime import timedelta, timezone, datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from pydantic import ValidationError
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from config import settings
from auth.schemas import TokenData
from fastapi.security import OAuth2PasswordBearer


JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
EXPIRY_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

serializer = URLSafeTimedSerializer(
    secret_key=settings.JWT_SECRET, salt="email.configuration"
)


def create_access_token(
    user_data: dict,
    expires_delta: timedelta = timedelta(minutes=EXPIRY_MINUTES),
    refresh: Optional[bool] = False,
):
    to_encode = user_data.copy()
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "refresh": refresh, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("username")
        jti= payload.get("jti")
        expire= payload.get("exp")
        is_admin= payload.get("is_admin")


        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        return TokenData(user_id=user_id, username=username, jti=jti, expires_delta=expire, is_admin=is_admin)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired token"
        )


def create_url_safe_token(
    data: dict, expiry: int = 86400
):  # Default expiry: 24 hours (86400 seconds)
    data["exp"] = expiry
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str, max_age: int = 86400):
    try:
        token_data = serializer.loads(token, max_age=max_age)
        return token_data

    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired"
        )

    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )