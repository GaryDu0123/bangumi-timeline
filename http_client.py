# hoshino/modules/bangumi/http_client.py
from __future__ import annotations

import json

import aiohttp
from . import config

class HttpClient:
    def __init__(self):
        self._sess = None

    async def __aenter__(self):
        self._sess = aiohttp.ClientSession(headers={"User-Agent": config.USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._sess:
            await self._sess.close()

    async def get_text(self, url: str) -> str:
        assert self._sess is not None
        async with self._sess.get(url, timeout=config.TIMEOUT_SEC) as resp:
            resp.raise_for_status()
            return await resp.text()

