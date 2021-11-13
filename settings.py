from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    OUTPUT_BASE_PATH: str
    STORAGE_SERVICE_ENDPOINT: str
    DELTA_MINUTES_BEFORE_NOW: Optional[int] = 5