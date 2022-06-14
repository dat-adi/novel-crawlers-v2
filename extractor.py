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

# Importing the zipfile creation module
import zipfile

# Importing system modules for file handling
from pathlib import Path
import os

# Importing the query utility
from utilities import queryIt

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
        chapter_tag = soup.find("article", "post") or soup.find("article", "page")

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

def storeIt(chapter_title: str, content: str, output_folder: Path) -> Path:
    """Stores the chapters into xhtml files"""
    file_name_out = output_folder.joinpath("twi-" + str(chapter_title) + ".xhtml")
    f = open(file_name_out, "w", encoding="utf-8")
    f.write(content)
    f.close()
    return file_name_out

def generate_structure(titles: list, html_files: list, output_folder: Path):
    """Generates the structure for the EPUB file"""
    epub = zipfile.ZipFile(output_folder.joinpath("The Wandering Inn" + ".epub"), "w")
    novelname = "The Wandering Inn"
    author = "pirateaba"
    
    # Writing in the structure for the epub file
    epub.writestr("mimetype", "application/epub+zip")
    epub.writestr(
        "META-INF/container.xml",
        """<container version="1.0"
    xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
            <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
    </container>""",
    )

    index_tpl = """<package version="3.1" xmlns="http://www.idpf.org/2007/opf">
    <metadata>
        %(metadata)s
    </metadata>
    <manifest>
        %(manifest)s
    </manifest>
    <spine>
        <itemref idref="toc" linear="no"/>
        %(spine)s
    </spine>
</package>"""
    manifest = ""
    spine = ""

    metadata = """<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">%(novelname)s</dc:title>\n<dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="http://www.idpf.org/2007/opf" ns0:role="aut" ns0:file-as="NaN">%(author)s</dc:creator>\n<meta xmlns:dc="http://purl.org/dc/elements/1.1/" name="calibre:series" content="%(series)s"/>""" % {
        "novelname": novelname,
        "author": author,
        "series": novelname,
    }

    toc_manifest = '<item href="toc.xhtml" id="toc" properties="nav" media-type="application/xhtml+xml"/>'

    for i, html in enumerate(html_files):
        basename = os.path.basename(html)
        manifest += (
            '<item id="file_%s" href="%s" media-type="application/xhtml+xml"/>\n'
            % (i + 1, basename)
        )
        spine += '<itemref idref="file_%s" />' % (i + 1)
        epub.write(html, "OEBPS/" + basename)

    epub.writestr(
        "OEBPS/content.opf",
        index_tpl
        % {
            "metadata": metadata,
            "manifest": manifest + toc_manifest,
            "spine": spine,
        },
    )

    toc_start = """<?xml version='1.0' encoding='utf-8'?>
    <!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
        <head>
            <title>%(novelname)s</title>
        </head>
            <body>
                <section class="frontmatter TableOfContents">
            <header>
                <h1>Contents</h1>
            </header>
                <nav id="toc" role="doc-toc" epub:type="toc">
                    <ol>
                        %(toc_mid)s
                        %(toc_end)s"""
    toc_mid = ""
    toc_end = """</ol></nav></section></body></html>"""

    for i, y in enumerate(html_files):
        chapter = titles[i]
        chapter = str(chapter)
        toc_mid += """<li class="toc-Chapter-rw" id="num_%s">
                    <a href="%s">%s</a>
                    </li>""" % (
            i,
            os.path.basename(y),
            chapter,
        )

    epub.writestr(
        "OEBPS/toc.xhtml",
        toc_start % {"novelname": novelname, "toc_mid": toc_mid, "toc_end": toc_end},
    )
    epub.close()

def get_all_chapters() -> None:
    """Function that scrapes the entire wandering inn"""
    conn = redis.Redis()
    for link in range(conn.llen("chapter_links")):
        cleanIt(str(conn.lindex("chapter_links", link).decode()))

def generate_epub() -> None:
    """Functions that generates an EPUB file"""
    conn = redis.Redis()
    output_folder = (Path.cwd()).joinpath(Path('./output/'))

    # TODO: An improvement that can be made to the existing model is 
    # to also take in the file_path into the dictionary if it exists.
    # That way, we can get rid of the file_list variable altogether.
    file_list = []
    titles = []
    for link in queryIt():
        tmp = conn.get(link)
        tmp = json.loads(tmp)
        chapter_title = tmp["chapter_title"]
        content = tmp["content"]
        titles.append(tmp["chapter_title"])
        file_list.append(storeIt(chapter_title, content, output_folder))

    generate_structure(titles, file_list, output_folder)


if __name__ == "__main__":
    cleanIt("https://wanderinginn.com/interlude-satar-revised/")
