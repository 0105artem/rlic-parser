from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from db.dals.user_dal import UserDAL
from db.dependencies import get_user_dal
from schemas import user_schemas
from common import oauth2, utils

router = APIRouter(
    tags=['Authentication']
)


@router.post('/login', response_model=user_schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
                user_dal: UserDAL = Depends(get_user_dal)):
    user = await user_dal.get_user_by(login=user_credentials.username)

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid credentials!")

    if not await utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid credentials!")

    access_token = await oauth2.create_access_token(data={"username": user.login})

    return {"access_token": access_token, "token_type": "bearer"}
