from db.models.models import ParsingStatistics
from schemas import statistics_schema
from db.config import async_session


class StatisticsDAL:
    @async_session
    async def create(self, session, stat: statistics_schema.Statistics) -> None:
        new_card = ParsingStatistics(**stat.dict())
        session.add(new_card)
        await session.commit()
