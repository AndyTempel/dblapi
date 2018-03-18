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
    """
    Avatar object for easy to use interface. Get url by simply using :any:`url` method.
    If called as a string outputs .png url. You can get .gif if you use :any:`gif` method and
    you can resize image by using :any:`size` method.

    Parameters
    -----------
    img_hash: :class:`str`
        Avatar hash from discord.
    bot_id: :class:`int`
        Bot Client ID

    Attributes
    -----------
    hash: :class:`str`
        Avatar hash
    base_url: :class:`str`
        Base URL for avatar image without file suffix.
    """

    def __init__(self, img_hash, bot_id: int):
        """

        :param img_hash:
        :param bot_id:
        """
        self.hash = img_hash
        self.base_url = f"https://cdn.discordapp.com/avatars/{bot_id}/{self.hash}"

    @property
    def url(self):
        """
        Returns .png URL of bots/users avatar.

        :return: :class:`str`
            URL of the .png avatar image.
        """
        return self.base_url + ".png"

    def __str__(self):
        """
        Same as :any:`url`. Returns .png URL of bots/users avatar.

        :return: :class:`str`
            URL of the .png avatar image.
        """
        return self.base_url + ".png"

    @property
    def gif(self):
        """
        Returns .gif URL of bots/users avatar. IF user does not have animated avatar
        this method will produce URL that will get 404 error.

        :return: :class:`str`
            URL of the .gif avatar animation.
        """
        return self.base_url + ".gif"

    def size(self, size: int):
        """
        Returns URL of the resized avatar image as specified.

        :param size: :class:`int`
            Size of the image in pixels. Min 16, max 2048.
        :return: :class:`str`
            URL of the resized image.
        """
        return self.base_url + f".png?size={size}"


class Description:
    """
    Represents bot's description. By default returns short description, because long description is not required
    and can be blank.

    Attributes
    -------------
    short: :class:`str`
        Short description
    long: :class:`str`
        Long description

    """

    def __init__(self, short, long):
        self.short = short
        self.long = long

    def __get__(self, instance, owner):
        """
        If :class:`Description` accessed returns short description.

        :return: :class:`str`
            Short descriptions
        """
        return self.short

    def __str__(self):
        """
        If :class:`Description` accessed as string returns short description.

        :return: :class:`str`
            Short descriptions
        """
        return self.short


class DBLStats:
    """
    Represents statistics object of a discord bot.

    Attributes
    -------------
    server_count: :class:`str`
        Returns server count.
    shard_count: :class:`str`
        Returns shard count.
    shards: :class:`list`
        Returns list of shards.

    """

    def __init__(self, data):
        self.server_count = data.get("server_count", "N/A")
        self.shard_count = data.get("shard_count", "N/A")
        self.shards = data.get("shards", [])


class DBLBot:
    """
    Represents DBL bot object.

    Attributes
    ----------
    id: :class:`int`
        Bot Client ID
    username: :class:`str`
        Bot's username
    discriminator: int
        Bot's discriminator
    username_full: :class:`str`
        Full bot's username. Username#1234
    mention: :class:`str`
        Discord mention.
    avatar: :class:`Avatar`
        Returns :class:`Avatar` object.
    library: :class:`str`
        Bot's library
    prefix: :class:`str`
        Bot's prefix
    description: :class:`Description`
        Returns :class:`Description` object.
    tags: :class:`list`
        Returns list of tags
    owners: :class:`list`
        Returns list of owners
    approved_date: :class:`datetime.Datetime`
        Returns :class:`Datetime` object.
    is_certified: :class:`bool`
        Boolean. True if bot is certified, False otherwise
    votes: :class:`int`
        Bot's vote count
    website: :class:`str`
        Bot's website
    github: :class:`str`
        Bot's GitHub page
    link: :class:`str`
        Bot's DBL link. Prefers vanity URL
    invite: :class:`str`
        Bot's invite link
    support: :class:`str`
        Bot's support server URL

    """

    def __init__(self, snowflake: str, username: str, discriminator: str, def_avatar: str, lib: str, prefix: str,
                 short_desc: str, tags: list, owners: list, date: str, certified: bool, votes: int, other, client):
        self.client = client
        self.id = int(snowflake)
        self.username = username
        self.discriminator = int(discriminator)
        self.username_full = f"{self.username}#{self.discriminator}"
        self.mention = f"<@{self.id}>"
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
        """|coro|

        Gets bot's statistics from DBL.

        :return: :class:`DBLStats`
            Returns :class:`DBLStats` object.
        """
        r = await self.client.http.get(self.client.router.bot_stats.format_url(self.id))
        return DBLStats(r)
