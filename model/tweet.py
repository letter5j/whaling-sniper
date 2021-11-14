from datetime import datetime

from pydantic import BaseModel


class Tweet(BaseModel):
    id: str
    created_at: datetime
    text: str
