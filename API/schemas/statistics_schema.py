from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StatisticsBase(BaseModel):
    pass


class StatisticsDB(StatisticsBase):
    id: int
    table: str
    task_id: str
    num_results: Optional[int] = None
    status: str
    details: Optional[str] = None
    csv_file: Optional[str] = None
    started: Optional[datetime] = None
    ended: Optional[datetime] = None

    class Config:
        orm_mode = True
