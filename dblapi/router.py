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

from .errors import RequireFormatting


class Route(object):
    def __init__(self, url: str, method: str, require_format: bool = False):
        self.url = url
        self.method = method
        self.require_format = require_format

    def __str__(self) -> str:
        if self.require_format:
            raise RequireFormatting
        return self.url

    def __get__(self, instance, owner) -> str:
        if self.require_format:
            raise RequireFormatting
        return self.url

    def format_url(self, *args) -> str:
        return self.url.format(*args)


class Router(object):
    def __init__(self, base_url: str):
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.base_bot = base_url + "bots"
        self.base_usr = base_url + "users/"
        self.base_wig = base_url + "widget/"

        self.bot_search = Route(self.base_bot, "GET")
        self.bot_get = Route(self.base_bot + "/{}", "GET", True)
        self.bot_votes = Route(self.base_bot + "/{}/votes", "GET", True)
        self.bot_stats = Route(self.base_bot + "/{}/stats", "GET", True)
        self.bot_ul_stats = Route(self.base_bot + "{}/stats", "POST", True)

        self.user_get = Route(self.base_usr + "{}", "GET", True)

        self.widget_get = Route(self.base_wig + "{}.svg", "GET", True)
        self.widget_owner = Route(self.base_wig + "owner/{}.svg", "GET", True)

