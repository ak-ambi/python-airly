import json

import aiohttp
import logging

from airly.exceptions import AirlyError

_LOGGER = logging.getLogger(__name__)


class _EmptyFormat:
    def __format__(self, format_spec):
        return ''


class _RequestsHandler:
    """Internal class to create Airly requests"""

    def __init__(self, api_key, session: aiohttp.ClientSession, base_url,
                 language=None):
        self.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'apikey': api_key,
        }
        if language is not None:
            self.headers['Accept-Language'] = language
        self.base_url = base_url
        self.session = session

    async def get(self, request_path):
        url = self.base_url + request_path
        _LOGGER.debug("Sending request: " + url)
        async with self.session.get(url, headers=self.headers) as response:
            if response.status != 200:
                _LOGGER.warning("Invalid response from Airly API: %s",
                                response.status)
                raise AirlyError(response.status, await response.text())

            data = await response.json()
            _LOGGER.debug(json.dumps(data))
            return data

class _DictToObj(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)
