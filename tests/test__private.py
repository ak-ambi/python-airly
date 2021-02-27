import json
from unittest import TestCase

import aiohttp
from aioresponses import aioresponses
from aiounittest import AsyncTestCase

from airly import Airly
from airly._private import _DictToObj

LATITUDE = 12
LONGITUDE = 21

class _DictToObjTestCase(TestCase):
    def test_init_with_iterable(self):
        data = { 'key1': 'value1', 'key2': 2 }
        sut = _DictToObj(data)
        self.assertEqual('value1', sut['key1'])
        self.assertEqual('value1', sut.key1)
        self.assertEqual(2, sut['key2'])
        self.assertEqual(2, sut.key2)

    def test_init_with_kwargs(self):
        sut = _DictToObj(key1='value1', key2=2)
        self.assertEqual('value1', sut['key1'])
        self.assertEqual('value1', sut.key1)
        self.assertEqual(2, sut['key2'])
        self.assertEqual(2, sut.key2)


class RemainingRequestsTestCase(AsyncTestCase):
    async def test_valid_remaining_requests_headers(self):
        with open("data/measurements_typical.json") as file:
            data = json.load(file)
        headers = {"X-RateLimit-Limit-day": "1000", "X-RateLimit-Remaining-day": "993"}

        session = aiohttp.ClientSession()

        with aioresponses() as session_mock:
            session_mock.get(
                'https://airapi.airly.eu/v2/measurements/point?lat=12.000000&lng=21.000000',
                payload=data,
                headers=headers,
            )
            airly = Airly("abcdef", session)
            measurements = airly.create_measurements_session_point(LATITUDE, LONGITUDE)
            await measurements.update()

        await session.close()

        self.assertEqual(1000, airly.requests_per_day)
        self.assertEqual(993, airly.requests_remaining)

    async def test_invalid_remaining_requests_headers(self):
        with open("data/measurements_typical.json") as file:
            data = json.load(file)
        headers = {}
        
        session = aiohttp.ClientSession()

        with aioresponses() as session_mock:
            session_mock.get(
                'https://airapi.airly.eu/v2/measurements/point?lat=12.000000&lng=21.000000',
                payload=data,
                headers=headers,
            )
            airly = Airly("abcdef", session)
            measurements = airly.create_measurements_session_point(LATITUDE, LONGITUDE)
            await measurements.update()
        
        await session.close()

        self.assertIsNone(airly.requests_per_day)
        self.assertIsNone(airly.requests_remaining)
        