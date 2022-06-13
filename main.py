#!venv/bin/python
"""
The main program to run the Novel Crawlers FastAPI application.
"""
# Web crawler built to get the wandering inn to your doorstep.
# Copyright © 2022 Datta Adithya G V <dat.adithya@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Importing FastAPI tools
from fastapi import FastAPI
from pydantic import BaseModel

# Importing Redis and Redis Queue
import redis
from rq import Queue

# Importing the components
from indexer import indexIt, queryIt, flushIt
from extractor import cleanIt

# Importing the AGSI web server
import uvicorn


# Initializing default values for configuration variables
# TODO: Make all of this dynamic and loaded from config files.
app = FastAPI()
redis_conn = redis.Redis(host='localhost', port=6379)
queue = Queue(connection=redis_conn)
queue.empty()

# Defining an IndexList
class IndexList(BaseModel):
    ChapterName: dict

@app.get('/index')
async def index() ->  IndexList:
    """Index the Table of Contents Page"""
    job = queue.enqueue(indexIt)
    return job.result

@app.get('/chapters')
async def list_chapters() -> None:
    """List the various chapters in the terminal space"""
    queue.enqueue(queryIt)

@app.get('/flushall')
async def flush_all() -> str:
    """Flushing the database"""
    queue.enqueue(flushIt)
    return "Successful Flush"

@app.get('/generate')
async def generate() -> str:
    """Component to generate the Wandering Inn EPUB"""
    return "Under construction"

@app.get('/wordcount')
async def word_count() -> str:
    """Get the word counts for the different chapters"""
    return "Under development"

if __name__ == "__main__":
    """Run the uvicorn ASGI web server"""
    uvicorn.run(app, host="0.0.0.0", port=10000)
