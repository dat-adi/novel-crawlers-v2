import requests
import json
import redis
from bs4 import BeautifulSoup

def indexIt():
    conn = redis.Redis()
    page = requests.get("https://wanderinginn.com/table-of-contents/").text
    soup = BeautifulSoup(page, "html.parser")
    contents_tag = soup.find("div", "entry-content")
    chapter_links = [link.get("href") for link in contents_tag.find_all("a")]

    for link in chapter_links:
        if link[-1] != "/":
            link += "/"
        if link[-2:] == "//":
            link = link[:-1]

    conn.set("chapter_links", str(chapter_links))
    for link in chapter_links:
        conn.set(link, json.dumps({"chapter_url": link}))

    return chapter_links

def queryIt():
    conn = redis.Redis()
    print(conn.get('1-01'))
    print(conn.keys())
    print(conn.get("chapter_links"))

def flushIt():
    conn = redis.Redis()
    conn.flushall()

if __name__ == "__main__":
    indexIt()
