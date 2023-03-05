from typing import List

from fastapi import status, Depends, APIRouter, HTTPException, Response

from db.dals.user_dal import UserDAL
from db.dependencies import get_user_dal
from schemas import user_schemas
from common import utils, oauth2

router = APIRouter(
    prefix="/users",
    tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserResponse)
async def create_user(user: user_schemas.CreateUser, user_dal: UserDAL = Depends(get_user_dal),
                      validation=Depends(oauth2.validate_user)):
    user.password = await utils.create_hash(user.password)
    new_user = await user_dal.create_user(user)
    return new_user


@router.get("/", response_model=List[user_schemas.UserResponse])
async def get_all_users(user_dal: UserDAL = Depends(get_user_dal),
                        validation=Depends(oauth2.validate_user)):
    return await user_dal.get_all_users()


@router.get("/{username}", response_model=user_schemas.UserResponse)
async def get_user(login: str, user_dal: UserDAL = Depends(get_user_dal),
                   validation=Depends(oauth2.validate_user)):
    user = await user_dal.get_user_by(login=login)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with login {login} was not found")

    return user


@router.patch("/{username}", response_model=user_schemas.UserResponse)
async def update_user(user: user_schemas.UpdateUser, user_dal: UserDAL = Depends(get_user_dal),
                      validation=Depends(oauth2.validate_user)):
    exists = await user_dal.get_user_by(login=user.login)

    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with login {user.login} was not found")
    return await user_dal.update_user(user)


@router.delete("/{username}")
async def delete_post(login: str, user_dal: UserDAL = Depends(get_user_dal),
                validation=Depends(oauth2.validate_user)):
    exists = await user_dal.get_user_by(login=login)

    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with login {login} was not found")

    await user_dal.delete_user(login=login)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
