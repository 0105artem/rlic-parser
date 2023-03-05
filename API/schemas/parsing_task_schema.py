from typing import Optional

from pydantic import BaseModel


class ParsingTask(BaseModel):
    task_id: Optional[str] = None
    status: str
    started: Optional[str] = None
    ended: Optional[str] = None
    num_results: Optional[str] = None
    details: Optional[str] = None
