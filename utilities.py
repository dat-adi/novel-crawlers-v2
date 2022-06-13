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

    for link in chapter_links:
        if len(link[25:].split('/')) > 2:
            conn.set(link[25:].split('/')[3], json.dumps({"chapter_url": link}))
        else:
            conn.set(link[25:].split('/')[0], json.dumps({"chapter_url": link}))

    return chapter_links

def queryIt():
    conn = redis.Redis()
    print(conn.get('1-01'))
    print(conn.get('*'))

if __name__ == "__main__":
    indexIt()
