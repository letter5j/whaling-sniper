import datetime
from typing import List

from pydantic import BaseModel


class Tweet(BaseModel):
    id: int
    conversation_id: str
    created_at: str
    date: datetime.date
    time: datetime.time
    timezone: str
    user_id: int
    username: str
    name: str
    place: str
    tweet: str
    language: str
    mentions: List[str]
    urls: List[str]
    photos: List[str]
    replies_count: int
    retweets_count: int
    likes_count: int
    hashtags: List[str]
    cashtags: List[str]
    link: str
    retweet: bool
    quote_url: str
    video: int
    thumbnail: str
    near: str
    geo: str
    source: str
    user_rt_id: str
    user_rt: str
    retweet_id: str
    reply_to: List[str]
    retweet_date: str
    translate: str
    trans_src: str
    trans_dest: str
