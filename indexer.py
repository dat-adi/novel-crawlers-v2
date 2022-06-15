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
    for link in chapter_links:
        conn.rpush("chapter_links", link)
        conn.set(link, json.dumps({"chapter_url": link}))

    return chapter_links


def count_words() -> dict:
    conn = redis.Redis()
    res = {}
    total_word_count = 0

    for link in range(conn.llen("chapter_links")):
        tmp = str(conn.lindex("chapter_links", link).decode())
        tmp = json.loads(conn.get(tmp))

        chapter_title = tmp["chapter_title"]
        word_count = tmp["word_count"]
        total_word_count += word_count

        res[chapter_title] = word_count

    res["Total Word Count"] = total_word_count
    res["Total Page Count"] = total_word_count // 233

    return res


if __name__ == "__main__":
    indexIt()
