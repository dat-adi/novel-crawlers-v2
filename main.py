from fastapi import FastAPI
from pydantic import BaseModel
import redis
from rq import Queue
from utilities import indexIt, queryIt
import uvicorn


app = FastAPI()
redis_conn = redis.Redis(host='localhost', port=6379)
queue = Queue(connection=redis_conn)
queue.empty()

class IndexList(BaseModel):
    ChapterName: dict


@app.get('/index')
async def index() ->  IndexList:
    job = queue.enqueue(indexIt)
    return job.result

@app.get('/chapters')
async def list_chapters() -> None:
    queue.enqueue(queryIt)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
