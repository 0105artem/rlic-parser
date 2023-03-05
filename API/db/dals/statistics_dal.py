from sqlalchemy import select, update
from sqlalchemy.orm import Session

from db.models.models import ParsingStatistics
from schemas import statistics_schema


class StatisticsDAL:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    async def get_latest_parsing(self, table: str) -> statistics_schema.StatisticsDB | None:
        stmt = (
            select(ParsingStatistics)
            .where((ParsingStatistics.status == 'done') &
                   (ParsingStatistics.table == table))
            .order_by(ParsingStatistics.started.asc())
            .limit(1)
        )
        res = await self.db_session.execute(stmt)
        if res:
            return statistics_schema.StatisticsDB(**res.scalars().first().__dict__)

    async def set_csv_file(self, task_id: str, csv_filename: str):
        stmt = (
            update(ParsingStatistics)
            .where(ParsingStatistics.task_id == task_id)
            .values(csv_file=csv_filename)
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
