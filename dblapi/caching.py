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
import datetime


class Cacher:
    def __init__(self, client, update_function, store_for: int = 10, is_dict: bool = True, **kwargs):
        self.client = client
        self.store = {} if is_dict else []
        self.store_for = datetime.timedelta(seconds=store_for)
        self.expiry = datetime.datetime.utcnow()
        self.kwargs = kwargs

        self.update_cache = update_function

    def set_expiry(self):
        self.expiry = datetime.datetime.utcnow() + self.store_for

    @property
    async def get(self):
        if datetime.datetime.utcnow() > self.expiry:
            self.store.clear()
            self.store = await self.update_cache(self.client, self.kwargs)
            self.set_expiry()
        return self.store

    def __set__(self, instance, value):
        self.store.clear()
        self.store = value
        self.set_expiry()

    async def get_val(self, key):
        if datetime.datetime.utcnow() > self.expiry:
            self.store.clear()
            self.store = await self.update_cache(self.client, self.kwargs)
            self.set_expiry()
        return self.store[key]

    async def remove_val(self, key):
        if datetime.datetime.utcnow() > self.expiry:
            self.store.clear()
            self.store = await self.update_cache(self.client, self.kwargs)
            self.set_expiry()
        del self.store[key]

    async def append(self, value):
        if datetime.datetime.utcnow() > self.expiry:
            self.store.clear()
            self.store = await self.update_cache(self.client, self.kwargs)
            self.set_expiry()
        self.store.append(value)

    async def update(self, key, value):
        if datetime.datetime.utcnow() > self.expiry:
            self.store.clear()
            self.store = await self.update_cache(self.client, self.kwargs)
            self.set_expiry()
        self.store.update({key: value})

    async def is_in(self, key):
        if datetime.datetime.utcnow() > self.expiry:
            self.store.clear()
            self.store = await self.update_cache(self.client, self.kwargs)
            self.set_expiry()
        if key in self.store:
            return True
        else:
            return False
