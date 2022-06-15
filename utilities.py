#!venv/bin/python
"""
The program set up for utilities.
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
# Importing redis
import redis


def queryIt():
    """A utility function to query for all the chapter records in the database"""
    conn = redis.Redis()
    print(conn.get("1-01"))
    print(conn.keys())
    # TODO: Seems inefficient to access the database these many times,
    # check to see if there's a better solution.
    for link in range(conn.llen("chapter_links")):
        print(str(conn.lindex("chapter_links", link).decode()))

    return [
        str(conn.lindex("chapter_links", link).decode())
        for link in range(conn.llen("chapter_links"))
    ]


def flushIt():
    """A utility function that flushes the database"""
    conn = redis.Redis()
    conn.flushall()
