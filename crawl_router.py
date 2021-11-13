import asyncio
import datetime
import io
import json
import os.path
import sys
import uuid
from typing import List

import aiohttp
import twint
from fastapi import APIRouter, HTTPException
from starlette import status

from settings import Settings
from model.crawl_job import CrawlJobCreateDto
from model.tweet import Tweet

setting = Settings()
CrawlRouter = APIRouter()


async def post(session, tweet: Tweet):
    async with session.post(setting.STORAGE_SERVICE_ENDPOINT, data=tweet.json()) as response:
        return response


async def send_to_storage(tweets: List[Tweet]):
    async with aiohttp.ClientSession() as session:
        tasks = [post(session, tweet) for tweet in tweets]
        await asyncio.gather(*tasks)


@CrawlRouter.post("/crawl", status_code=status.HTTP_201_CREATED)
async def create_crawl_job(crawl_job_create_dto: CrawlJobCreateDto):
    print(
        f"User: {crawl_job_create_dto.username}, Start Date: {crawl_job_create_dto.start_date}, End Date: {crawl_job_create_dto.end_date}")

    # Configure
    id: str = str(uuid.uuid4())
    output_path: str = os.path.join(setting.OUTPUT_BASE_PATH, id + ".json")
    twint_config = twint.Config()
    twint_config.Username = crawl_job_create_dto.username
    twint_config.Since = crawl_job_create_dto.start_date
    twint_config.Until = crawl_job_create_dto.end_date
    if crawl_job_create_dto.start_date is None and crawl_job_create_dto.end_date is None:
        now: datetime.datetime = datetime.datetime.now()
        twint_config.Until = now.strftime("%Y-%m-%d %H:%M:%S")
        twint_config.Since = (now - datetime.timedelta(minutes=setting.DELTA_MINUTES_BEFORE_NOW)).strftime(
            "%Y-%m-%d %H:%M:%S")

    # "2021-11-08 14:20:00"

    print(f"Query: {twint_config.Username}, Since: {twint_config.Until}, Until: {twint_config.Since}")
    twint_config.Store_json = True
    twint_config.Output = output_path

    # Run
    print("Starting search.")
    twint.run.Search(twint_config)
    tweets: List[Tweet] = list()
    try:
        with io.open(output_path, 'rb+') as f:
            while line := f.readline():
                tweets.append(Tweet(**json.loads(line)))
    except RuntimeError as err:
        print(f"Unexpected error: {sys.exc_info()[0]} error: {err}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Parsing search result Unexpected error: {sys.exc_info()[0]} error: {err}.")
    except OSError as err:
        print(f"OS error: {sys.exc_info()[0]} error: {err}.")
        print("Probably no new Posts.")
    finally:
        print("Parsing search result finish.")
    try:
        print("Send to Storage Service.")
        await send_to_storage(tweets)
    except RuntimeError as err:
        print(f"Unexpected error: {sys.exc_info()[0]} error: {err}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Send to Storage Service Unexpected error: {sys.exc_info()[0]} error: {err}.")
    finally:
        print("Finish Request.")
    print(f"Tweets: {tweets}")
    return tweets
