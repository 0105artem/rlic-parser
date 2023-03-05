from typing import List

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models.models import License
from schemas import license_schema


class LicenseDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_num_rows(self):
        stmt = func.count(License.id)
        rows = await self.db_session.execute(stmt)
        return rows.first()[0]

    async def create_license(self, license: license_schema.License):
        new_license = License(**license.dict())
        self.db_session.add(new_license)
        try:
            await self.db_session.commit()
        except IntegrityError as ex:
            await self.db_session.rollback()
            logger.warning(f"License {new_license.license_id} already exists!")

    async def create_licenses(self, licenses: List[license_schema.License]):
        stmt = insert(License).values([lic.dict() for lic in licenses]).on_conflict_do_nothing()
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def get_license(self, license_id: str):
        q = await self.db_session.execute(select(License).where(License.license_id == license_id))
        return q.scalars().first()

    async def get_all_licenses(self, limit: int = None, offset: int = 0) -> List[license_schema.License]:
        if limit is None:
            limit = await self.get_num_rows()

        stmt = select(License).order_by(License.id).limit(limit).offset(offset)
        res = await self.db_session.execute(stmt)
        return res.scalars().all()
