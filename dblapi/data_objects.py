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

VALID_STATIC_FORMATS = {"jpeg", "jpg", "webp", "png"}
VALID_AVATAR_FORMATS = VALID_STATIC_FORMATS | {"gif"}


class Avatar:
    """
    Avatar object for easy to use interface. Get url by simply using :any:`url` method.
    If called as a string outputs .png url. You can get .gif if you use :any:`gif` method and
    you can resize image by using :any:`size` method.

    .. container:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: hash(x)

            Return the user's hash.

        .. describe:: str(x)

            Returns the user's name with discriminator.

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
    default_avatar_url: :class:`str`
        Returns URL of default avatar.
    """

    def __init__(self, img_hash, bot_id: int):
        """

        :param img_hash:
        :param bot_id:
        """
        self.hash = str(img_hash)
        self.base_url = f"https://cdn.discordapp.com/avatars/{bot_id}/{self.hash}"
        self.default_avatar_url = f"https://cdn.discordapp.com/embed/avatars/{bot_id % 5}.png"

    @property
    def url(self):
        """
        Returns URL of bots/users avatar.

        :return: :class:`str`
            URL of the .webp if avatar is not animated or .gif avatar is animated.
        """
        return self.url_as()

    @property
    def is_avatar_animated(self) -> bool:
        """
        Returns True if avatar is animated, False otherwise.

        :return: :class:`bool`
        """
        return self.hash.startswith("a_")

    def url_as(self, format: str = None, static_format: str = "webp", size: int = 1024) -> str:
        if not ((size != 0) and not (size & (size - 1))) and size in range(16, 1025):
            raise InvalidArgument("size must be a power of 2 between 16 and 1024")
        if format is not None and format not in VALID_AVATAR_FORMATS:
            raise InvalidArgument("format must be None or one of {}".format(VALID_AVATAR_FORMATS))
        if format == "gif" and not self.is_avatar_animated:
            raise InvalidArgument("non animated avatars do not support gif format")
        if static_format not in VALID_STATIC_FORMATS:
            raise InvalidArgument("static_format must be one of {}".format(VALID_STATIC_FORMATS))

        if self.hash is None:
            return self.default_avatar_url

        if format is None:
            if self.is_avatar_animated:
                format = 'gif'
            else:
                format = static_format

        gif_fix = '&_=.gif' if format == 'gif' else ''
        return "{0.base_url}.{1}?size={2}{3}".format(self, format, size, gif_fix)

    def __str__(self):
        """
        Same as :any:`url`. Returns .png URL of bots/users avatar.

        :return: :class:`str`
            URL of the .png avatar image.
        """
        return self.base_url + ".png"

    def __get__(self):
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
        Returns URL of the resized static avatar image as specified.

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
    discriminator: :class:`int`
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
        self._stats_got = False
        self._stats_obj = None

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
        if self._stats_got and self._stats_obj:
            return self._stats_obj
        else:
            r = await self.client.http.get(self.client.router.bot_stats.format_url(self.id))
            obj = DBLStats(r)
            self._stats_got = True
            self._stats_obj = obj
            return obj
