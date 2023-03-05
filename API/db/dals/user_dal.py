from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from db.models.models import User
from schemas import user_schemas


class UserDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(self, user: user_schemas.CreateUser) -> user_schemas.UserResponse:
        new_user = User(**user.dict())
        self.db_session.add(new_user)
        await self.db_session.flush()
        await self.db_session.refresh(new_user)
        return new_user

    async def get_user_by(self, user_id: Optional[int] = None, login: Optional[str] = None):
        if user_id:
            stmt = await self.db_session.execute(select(User).where(User.id == user_id))
            return stmt.scalars().first()
        elif login:
            stmt = await self.db_session.execute(select(User).where(User.login == login))
            return stmt.scalars().first()
        else:
            return None

    async def get_all_users(self) -> List[user_schemas.UserResponse]:
        stmt = await self.db_session.execute(select(User).order_by(User.id))
        return stmt.scalars().all()

    async def update_user(self, user: user_schemas.UpdateUser) -> user_schemas.UserResponse:
        stmt = update(User).where(User.login == user.login).returning(User)
        if user.id is not None:
            stmt = stmt.values(id=user.id)
        orm_stmt = (
            select(User)
            .from_statement(stmt)
            .execution_options(synchronize_session="fetch")
        )

        res = (await self.db_session.execute(orm_stmt)).scalars().first()
        await self.db_session.commit()
        return res

    async def delete_user(self, login: str):
        stmt = delete(User).where(User.login == login)
        stmt.execution_options(synchronize_session="fetch")
        await self.db_session.execute(stmt)
        await self.db_session.commit()
