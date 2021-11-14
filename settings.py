from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    TWITTER_BEARER_TOKEN: str
    OUTPUT_BASE_PATH: str
    STORAGE_SERVICE_ENDPOINT: Optional[str]
    DELTA_MINUTES_BEFORE_NOW: Optional[int] = 5
