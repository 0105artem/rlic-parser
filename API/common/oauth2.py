from datetime import datetime, timedelta

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from db.dals.user_dal import UserDAL
from db.dependencies import get_user_dal
from schemas import user_schemas
from settings import env

SECRET_KEY = env.SECRET_KEY
ALGORITHM = env.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(env.ACCESS_TOKEN_EXPIRE_MINUTES)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("username")

        if username is None:
            raise credentials_exception

        # Validate token fields by pydantic schema
        token_data = user_schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return token_data


async def validate_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    await verify_access_token(token, credentials_exception)


async def get_logged_user(token: str = Depends(oauth2_scheme),
                          user_dal: UserDAL = Depends(get_user_dal)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = await verify_access_token(token, credentials_exception)

    user = await user_dal.get_user_by(login=token.username)

    return user
