# The MIT License (MIT)
# Copyright (c) 2018 AndyTempel
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import dateutil.parser

from .errors import *


class Avatar:
    def __init__(self, img_hash, bot_id: int):
        self.hash = img_hash
        self.base_url = f"https://cdn.discordapp.com/avatars/{bot_id}/{self.hash}"

    @property
    def url(self):
        return self.base_url + ".png"

    def __str__(self):
        return self.base_url + ".png"

    @property
    def gif(self):
        return self.base_url + ".gif"

    def size(self, size: int):
        return self.base_url + f".png?size={size}"


class Description:
    def __init__(self, short, long):
        self.short = short
        self.long = long

    def __get__(self, instance, owner):
        return self.short

    def __str__(self):
        return self.short


class DBLStats:
    def __init__(self, data):
        self.server_count = data.get("server_count", "N/A")
        self.shard_count = data.get("shard_count", "N/A")
        self.shards = data.get("shards", [])


class DBLBot:
    def __init__(self, snowflake: str, username: str, discriminator: str, def_avatar: str, lib: str, prefix: str,
                 short_desc: str, tags: list, owners: list, date: str, certified: bool, votes: int, other, client):
        self.client = client
        self.id = int(snowflake)
        self.username = username
        self.discriminator = int(discriminator)
        self.username_full = f"{self.username}#{self.discriminator}"
        self.avatar = Avatar(other.get("avatar", def_avatar), self.id)
        self.library = lib
        self.prefix = prefix
        self.description = Description(short_desc, other.get("long_desc", ""))
        self.tags = tags
        self.owners = owners
        self.approved_date = dateutil.parser.parse(date)
        self.is_certified = certified
        self.votes = votes
        self.website = other.get("website", "")
        self.github = other.get("github", "")
        self.link = f"https://discordbots.org/bot/{other.get('vanity', self.id)}"
        self.invite = other.get("invite", "")
        self.support = f"https://discord.gg/{other.get('support', '')}"

    @classmethod
    def parse(cls, resp, client):
        try:
            data = cls(resp['id'], resp['username'], resp['discriminator'], resp['defAvatar'], resp['lib'],
                       resp['prefix'], resp['shortdesc'], resp['tags'], resp['owners'], resp['date'],
                       resp['certifiedBot'], resp['points'], resp, client)
        except KeyError:
            raise WeirdResponse
        else:
            return data

    @property
    async def stats(self) -> DBLStats:
        r = await self.client.http.get(self.client.router.bot_stats.format_url(self.id))
        return DBLStats(r)
