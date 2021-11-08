from pydantic import BaseSettings


class Settings(BaseSettings):
    OUTPUT_BASE_PATH: str
    STORAGE_SERVICE_ENDPOINT: str