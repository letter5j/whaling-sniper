import asyncio
import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

import aiohttp
import tweepy
from fastapi import APIRouter, HTTPException
from starlette import status
from tweepy import Client, User, errors, Response

from model.crawl_job import CrawlJobCreateDto
from model.tweet import Tweet
from settings import Settings

setting = Settings()
CrawlRouter = APIRouter()


async def post(session, tweet: Tweet):
    async with session.post(setting.STORAGE_SERVICE_ENDPOINT, data=tweet.json()) as response:
        return response


async def send_to_storage(tweets: List[Tweet]):
    async with aiohttp.ClientSession() as session:
        tasks = [post(session, tweet) for tweet in tweets]
        await asyncio.gather(*tasks)


@CrawlRouter.post("/crawl", status_code=status.HTTP_201_CREATED, response_model=List[Tweet])
async def create_crawl_job(crawl_job_create_dto: CrawlJobCreateDto):
    print(
        f"User: {crawl_job_create_dto.username}, "
        f"Start Date: {crawl_job_create_dto.start_date}, "
        f"End Date: {crawl_job_create_dto.end_date}")
    client = Client(
        bearer_token=setting.TWITTER_BEARER_TOKEN)
    print(f"Start to get user id by username: {crawl_job_create_dto.username}")
    user: Optional[User] = None
    try:
        user = client.get_user(username=crawl_job_create_dto.username)[0]
    except errors.BadRequest as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error: {err}.")
    except errors.Unauthorized as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error: {err}.")
    finally:
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Username {crawl_job_create_dto.username} not found.")
    print(f"UserName: {user.username}, User Show Name: {user.name}, User Id: {user.id}")

    utc_timezone = ZoneInfo('UTC')
    local_timezone = ZoneInfo('Asia/Taipei')
    end_time: datetime.datetime
    start_time: datetime.datetime

    end_time = datetime.datetime.strptime(
        crawl_job_create_dto.end_date, '%Y-%m-%d %H:%M:%S') \
        if crawl_job_create_dto.end_date else datetime.datetime.now()

    start_time = datetime.datetime.strptime(
        crawl_job_create_dto.start_date, '%Y-%m-%d %H:%M:%S') \
        if crawl_job_create_dto.start_date else end_time - datetime.timedelta(minutes=setting.DELTA_MINUTES_BEFORE_NOW)

    start_localtime = start_time.replace(tzinfo=local_timezone)
    end_localtime = end_time.replace(tzinfo=local_timezone)
    start_utctime = start_time.astimezone(utc_timezone)
    end_utctime = end_time.astimezone(utc_timezone)
    print(
        f"Query "
        f"since: {start_localtime.isoformat(timespec='seconds')}, "
        f"until: {end_localtime.isoformat(timespec='seconds')}")
    print(
        f"Query UTC "
        f"since: {start_utctime.isoformat(timespec='seconds')}, "
        f"until: {end_utctime.isoformat(timespec='seconds')}")

    try:
        response: Response = client.get_users_tweets(id=user.id, start_time=start_utctime.isoformat(timespec='seconds'),
                                                     end_time=end_utctime.isoformat(timespec='seconds'),
                                                     tweet_fields=["id", "text", "created_at"]
                                                     )
    except errors.BadRequest as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error: {err}.")
    except errors.Unauthorized as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error: {err}.")
    response_tweets: Optional[List[tweepy.Tweet]] = response.data
    tweets: List[Tweet] = list()
    if response_tweets is None:
        response_tweets = list()
        print("No tweets available.")
    for tweet in response_tweets:
        tweets.append(Tweet(id=tweet.id, created_at=tweet.created_at.replace(tzinfo=local_timezone), text=tweet.text))
    if setting.STORAGE_SERVICE_ENDPOINT:
        await send_to_storage(tweets)
    return tweets
