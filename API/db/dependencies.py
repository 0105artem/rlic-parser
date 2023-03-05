from db.config import AsyncLocalSession
from db.dals.license_dal import LicenseDAL
from db.dals.user_dal import UserDAL
from db.dals.statistics_dal import StatisticsDAL


async def get_license_dal():
    async with AsyncLocalSession() as session:
        async with session.begin():
            yield LicenseDAL(session)


async def get_user_dal():
    async with AsyncLocalSession() as session:
        async with session.begin():
            yield UserDAL(session)


async def get_statistics_dal():
    async with AsyncLocalSession() as session:
        async with session.begin():
            yield StatisticsDAL(session)
