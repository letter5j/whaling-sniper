import asyncio
import io
import json
import os.path
import uuid
from typing import List

import aiohttp
import nest_asyncio
import twint
from fastapi import APIRouter

from settings import Settings
from model.crawl_job import CrawlJobCreateDto
from model.tweet import Tweet

nest_asyncio.apply()
setting = Settings()
CrawlRouter = APIRouter()


async def post(session, tweet: Tweet):
    async with session.post(setting.STORAGE_SERVICE_ENDPOINT, data=tweet.json()) as response:
        return response


async def send_to_storage(tweets: List[Tweet]):
    async with aiohttp.ClientSession() as session:
        tasks = [post(session, tweet) for tweet in tweets]
        await asyncio.gather(*tasks)


@CrawlRouter.post("/crawl")
async def create_crawl_job(crawl_job_create_dto: CrawlJobCreateDto):
    # Configure
    id: str = str(uuid.uuid4())
    output_path: str = os.path.join(setting.OUTPUT_BASE_PATH, id + ".json")
    twint_config = twint.Config()
    twint_config.Username = crawl_job_create_dto.username
    twint_config.Since = crawl_job_create_dto.start_date
    if crawl_job_create_dto.end_date:
        twint_config.Until = crawl_job_create_dto.end_date
    # "2021-11-08 14:20:00"

    twint_config.Store_json = True
    twint_config.Output = output_path

    # Run
    twint.run.Search(twint_config)

    tweets: List[Tweet] = list()

    with io.open(output_path, 'rb+') as f:
        while line := f.readline():
            tweets.append(Tweet(**json.loads(line)))

    await send_to_storage(tweets)

    return {"OK", "OK"}



