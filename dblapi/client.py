# -*- coding: utf-8 -*-

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

import asyncio
import logging
import tempfile

import discord
from discord.ext.commands import Bot, AutoShardedBot
from diskcache import Cache

from .caching import Cacher
from .data_objects import *
from .helpers import *
from .request_lib import krequest
from .router import Router

BASE_URL = "https://discordbots.org/api/"
log = logging.getLogger(__name__)


class Client:
    """
    .. _event loop: https://docs.python.org/3/library/asyncio-eventloops.html
    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session


    Represents a client connection that connects to DBL API. It works in two modes:
        1. As a standalone variable.
        2. Plugged-in to discord.py Bot or AutoShardedBot, see `Client.pluggable`

    This class is used to interact with DBL API.


    Parameters
    -------------
    api_key: str
        Your DBL bot token.
    bot: Bot or AutoShardedBot
        Your bot client from discord.py
    disable_stats: bool[Optional]
        *Not required*
        Disable sending statistics from your bot to DBL.
        **Default:** False
    ssl_verify: bool[Optional]
        *Not required*
        Enable SSL certificate verification.
        **Default:** True
    **base_url: str[Optional]
        *Not required*
        Specify different DBL API url.
    **vote_days: int[Optional]
        *Not required*
        Specify how many days to look up votes. Defaults to 31.

    """
    def __init__(self, api_key: str, bot: Bot or AutoShardedBot, disable_stats: bool = False, ssl_verify: bool = True,
                 **kwargs):
        self.api_key = api_key
        self.http = krequest(global_headers=[
            ("Authorization", self.api_key)
        ])
        self.router = Router(kwargs.pop("base_url", BASE_URL))
        self.ssl_verify = ssl_verify

        self.bot = bot
        self.bot_id = None
        self.loop = kwargs.pop("loop", self.bot.loop)
        self.loop.create_task(self.__get_info())
        if not disable_stats:
            self.loop.create_task(self.__update_bot_stats())

        self.cache = Cache(tempfile.gettempdir())
        self.voting_cache = Cacher(self, update_vote_cache, is_dict=False, days=kwargs.get("vote_days", 31))

    async def __get_info(self):
        await self.bot.wait_until_ready()
        self.bot_id = self.bot.user.id
        log.debug(f"Got Bot user ID: {self.bot_id}")
        # log.info("Connecting to DBL and gathering information ...")

    async def __update_bot_stats(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            log.info("Posting bot statistics to DBL ...")
            try:
                data = {"server_count": len(self.bot.guilds)}
                if isinstance(self.bot, AutoShardedBot):
                    data.update({"shard_count": self.bot.shard_count, "shard_id": self.bot.shard_id})
                r = await self.http.post(self.router.bot_ul_stats.format_url(self.bot_id), json=data)
                log.debug(r)
            except Exception as e:
                log.error(e)
            finally:
                await asyncio.sleep(300)

    @classmethod
    def pluggable(cls, bot, api_key: str, *args, **kwargs):
        """
        Pluggable version of Client. Inserts Client directly into your Bot client.
        Called by using `bot.dbl`


        Parameters
        -------------
        api_key: str
            Your DBL bot token.
        bot: Bot or AutoShardedBot
            Your bot client from discord.py


        .. note::
            Takes the same parameters as :class:`Client` class.

        """
        try:
            return bot.dbl
        except AttributeError:
            bot.dbl = cls(api_key, bot=bot, *args, **kwargs)
            return bot.dbl

    async def has_user_voted(self, user: int or discord.User or discord.Member) -> bool:
        """|coro|

        Returns True if specified user has voted, False if not.
        Takes user parameter as int or discord.User or discord.Member


        Parameters
        --------------
        user: int, discord.User, discord.Member
            Specify user you want to check.


        :return: bool
        """
        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            user = user.id
        if str(user) in await self.voting_cache.get:
            return True
        else:
            return False

    async def iter_users_that_voted(self, iterable: bool = True):
        """|coro|

        If iterable parameter is True or not set outputs iterable for all users that have voted. If parameter set to False, returns list.


        Parameters
        --------------
        iterable: bool
            Should this function output an iterable.


        :return: list
        """
        if iterable:
            for user in await self.voting_cache.get:
                yield self.bot.get_user(int(user))
        else:
            yield await self.voting_cache.get

    async def search_bots(self, search: str, limit: int = 50, sort_by: str = None, offset: int = 0,
                          fields: str = None) -> list:
        """|coro|

        Search function for bots. Use search parameter to search for bots. This function returns DBLBot object.


        Parameters
        --------------
        search: str
            Search string
        limit: Optional[int]
            *Not required*
            Limit results to specified number. Cannot be negative. Max 500.
            **Default:** 50
        sort_by: Optional[str]
            *Not required*
            Sort bots by specified criteria.
        offset: Optional[int]
            *Not required*
            Offset output by specified number.
        fields: Optional[str]
            *Not required*
            Search specified comma-separated fields.


        :return: list
        """
        params = {
            "search": search,
            "limit": limit,
            "offset": offset
        }
        if sort_by:
            params.update({"sort": sort_by})
        if fields:
            params.update(({"fields": fields}))
        r = await self.http.get(self.router.bot_search, params=params)
        rdata = []
        for bot in r['results']:
            rdata.append(DBLBot.parse(bot, self))
        return rdata

    async def get_bot(self, bot_id: int) -> DBLBot:
        """|coro|

        Returns :class:`DBLBot` class of the specified bot ID.


        Parameters
        --------------
        bot_id: int
            Bot ID


        :return: DBLBot
        """
        r = await self.http.get(self.router.bot_get.format_url(bot_id))
        return DBLBot.parse(r, self)

    async def get_bot_stats(self, bot_id: int) -> DBLStats:
        """|coro|

        Returns :class:`DBLStats` class of the specified bot ID.


        Parameters
        --------------
        bot_id: int
            Bot ID


        :return: DBLStats
        """
        r = await self.http.get(self.router.bot_stats.format_url(bot_id))
        return DBLStats(r)
