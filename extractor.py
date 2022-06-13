#!venv/bin/python
"""
The program that extracts information from the pages of the book.
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

# Importing modules for web scraping
import requests
import json
from bs4 import BeautifulSoup

# Importing redis
import redis

def cleanIt(chapter_link: str):
    """Function that cleans up the page content"""
    conn = redis.Redis()
    tmp = conn.get(chapter_link)
    tmp = json.loads(tmp)

    # Checking if content is already present for the chapter
    # and skips cleaning if not required.
    if 'content' not in tmp.keys():
        # Raw data input
        raw = requests.get(tmp["chapter_url"]).text
        soup = BeautifulSoup(raw, "html.parser")
        chapter_tag = soup.find("article", "post")

        # Retrieving chapter title
        chapter_title = soup.find("h1", "entry-title")
        chapter_title = chapter_title.get_text()
        tmp["chapter_title"] = chapter_title
        print(chapter_title)

        # Main content retrieval
        text = chapter_tag.findChildren("p")

        # Word Counter
        word_count_text = text[:-1]
        word_count_text = str(text)
        word_count_text = word_count_text[1:-1]
        word_count_text = word_count_text.replace("<p>", "")
        word_count_text = word_count_text.replace("</p>,", "")
        word_count_text = word_count_text.replace("</p>", "")
        word_count_text = str(word_count_text)
        tmp["word_count"] = len(word_count_text.split()[:-4])

        # XHTML content setter
        text = str(text[:-1])[1:-1].replace("</p>,", "</p>\n")
        xhtml_code = '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: https://daisy.org/z3998/2012/vocab/structure/" lang="en" xml:lang="en">'
        xhtml_code += "\n<head>"
        xhtml_code += "\n<title>" + chapter_title + "</title>"
        xhtml_code += "\n</head>"
        xhtml_code += '\n<body dir="default">'
        xhtml_code += "\n<h1>" + chapter_title + "</h1>"
        xhtml_code += text
        xhtml_code += '\n</body>'
        xhtml_code += "\n</html>"
        tmp["content"] = xhtml_code

        # Converting the JSON content into string for storage
        tmp = json.dumps(tmp)
        conn.set(chapter_link, tmp)

def get_all_chapters() -> None:
    """Function that scrapes the entire wandering inn"""
    conn = redis.Redis()
    for link in range(conn.llen("chapter_links")):
        cleanIt(str(conn.lindex("chapter_links", link).decode()))

if __name__ == "__main__":
    cleanIt("https://wanderinginn.com/2016/07/27/1-00/")
