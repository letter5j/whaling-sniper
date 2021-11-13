from typing import Optional

from pydantic import BaseModel


class CrawlJobCreateDto(BaseModel):
    username: str
    start_date: Optional[str]
    end_date: Optional[str]
