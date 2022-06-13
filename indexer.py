#!venv/bin/python
"""
The component that indexes and stores the links to the chapters.
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

# Importing website parsing utilities
import requests
import json
from bs4 import BeautifulSoup

# Importing redis
import redis

def indexIt():
    """Function that scrapes and stores URLs from the Index"""
    conn = redis.Redis()

    # Retrieving all the data from the table of contents
    page = requests.get("https://wanderinginn.com/table-of-contents/").text
    soup = BeautifulSoup(page, "html.parser")

    # Retrieving only the chapter links from the content
    contents_tag = soup.find("div", "entry-content")
    chapter_links = [link.get("href") for link in contents_tag.find_all("a")]

    # Cleaning up broken links
    for link in chapter_links:
        if link[-1] != "/":
            link += "/"
        if link[-2:] == "//":
            link = link[:-1]

    # Entering the overall chapter links and the specific chapter links into
    # the Redis database.
    conn.set("chapter_links", str(chapter_links))
    for link in chapter_links:
        conn.set(link, json.dumps({"chapter_url": link}))

    return chapter_links

def queryIt():
    """A utility function to query for all the chapter records in the database"""
    conn = redis.Redis()
    print(conn.get('1-01'))
    print(conn.keys())
    print(conn.get("chapter_links"))

def flushIt():
    """A utility function that flushes the database"""
    conn = redis.Redis()
    conn.flushall()

if __name__ == "__main__":
    indexIt()
