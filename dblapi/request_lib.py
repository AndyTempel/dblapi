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

import sys
import traceback
import aiohttp

from dblapi import __version__


class krequest(object):
    def __init__(self, return_json=True, global_headers=[]):
        self.headers = {
            "User-Agent": "DBLAPI/{} (Github: AndyTempel) KRequests/alpha "
                          "(Custom asynchronous HTTP client)".format(__version__),
            "X-Powered-By": "Python {}".format(sys.version)
        }
        self.return_json = return_json
        for name, value in global_headers:
            self.headers.update({
                name: value
            })

    async def _proc_resp(self, response):
        if self.return_json:
            try:
                return await response.json()
            except Exception:
                print(traceback.format_exc())
                print(response)
                return {}
        else:
            return await response.text()

    async def get(self, url, params=None, headers=None, verify=True):
        headers = headers or {}
        headers.update(self.headers)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=verify)) as session:
            async with session.get(url, params=params, headers=headers) as resp:
                return await self._proc_resp(resp)

    async def delete(self, url, params=None, headers=None, verify=True):
        headers = headers or {}
        headers.update(self.headers)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=verify)) as session:
            async with session.delete(url, params=params, headers=headers) as resp:
                return await self._proc_resp(resp)

    async def post(self, url, data=None, json=None, headers=None, verify=True):
        headers = headers or {}
        headers.update(self.headers)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=verify)) as session:
            if json is not None:
                async with session.post(url, json=json, headers=headers) as resp:
                    return await self._proc_resp(resp)
            else:
                async with session.post(url, data=data, headers=headers) as resp:
                    return await self._proc_resp(resp)
