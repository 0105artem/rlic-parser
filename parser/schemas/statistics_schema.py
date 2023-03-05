from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Statistics(BaseModel):
    table: str
    task_id: str
    num_results: int
    status: str
    details: Optional[str]
    csv_file: Optional[str]
    started: Optional[datetime]
    ended: Optional[datetime]

    class Config:
        orm_mode = True

