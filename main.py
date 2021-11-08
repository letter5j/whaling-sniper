import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from crawl_router import CrawlRouter

app = FastAPI()
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(CrawlRouter, prefix="/api")

@app.get("/")
async def hello_word():
    return "Hello World."


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
