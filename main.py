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
import time
from fastapi import FastAPI
from pydantic import BaseModel

# Importing Redis and Redis Queue
import redis
from rq import Queue, Retry
from fastapi.responses import FileResponse

# Importing the components
from indexer import count_words, indexIt
from utilities.query import queryIt
from utilities.flush import flushIt
from extractor import download_and_clean, get_all_chapters, generate_epub

# Importing the AGSI web server
import uvicorn


# Initializing default values for configuration variables
# TODO: Make all of this dynamic and loaded from config files.
app = FastAPI()
redis_conn = redis.Redis()
queue = Queue(connection=redis_conn, default_timeout=3600)
queue.empty()


def report_success(job, connection, result, *args, **kwargs):
    print("Successful Job\n", job, connection, result)


def report_failure(job, connection, result, *args, **kwargs):
    print("Failure Management On-boarding bois.\n", job, connection, result)


@app.get("/index")
async def index() -> None:
    """Index the Table of Contents Page"""
    queue.enqueue(indexIt)


@app.get("/chapters")
async def list_chapters() -> None:
    """List the various chapters in the terminal space"""
    queue.enqueue(queryIt)


@app.get("/scrape")
async def scrape_all_chapters() -> None:
    """Scrape the wandering inn"""
    job = queue.enqueue(get_all_chapters)

    time.sleep(5)

    print(f"Done scraping!, {job.get_status()}")


@app.get("/flushall")
async def flush_all() -> str:
    """Flushing the database"""
    queue.enqueue(flushIt)
    return "Successful Flush"


@app.get("/generate")
async def generate() -> str:
    """Component to generate the Wandering Inn EPUB"""
    initial_time = time.time()
    queue.enqueue(generate_epub)
    end_time = time.time()

    return f"Generation of the EPUB has been done in {end_time - initial_time} seconds."


@app.get("/download")
async def download() -> FileResponse:
    queue.enqueue(download_and_clean, job_id="download_and_clean_job")
    # Placing sleep timer as 1, if the process takes any longer
    # than that, there's something wrong with the code.
    time.sleep(1)
    return FileResponse(
        path="/tmp/TWI/The Wandering Inn.epub",
        filename="TheWanderingInn.epub",
        media_type="text/epub",
    )


@app.get("/wordcount")
async def word_count() -> dict:
    """Get the word counts for the different chapters"""
    job = queue.enqueue(count_words)
    # Placing sleep timer as 1, this acts as a buffer for
    # the execution of the job, if the process takes any longer
    # than that, there's something wrong with the code.
    time.sleep(1)
    return job.result


if __name__ == "__main__":
    """Run the uvicorn ASGI web server"""
    uvicorn.run(app, host="127.0.0.1", port=10000)
