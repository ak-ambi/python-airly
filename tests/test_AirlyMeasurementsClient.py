import asyncio
import json
from unittest import TestCase

from airly import AirlyMeasurementsClient


class AirlyRequestsFactoryMock:
    def __init__(self, test_case: TestCase, expected_path, response):
        self.test_case = test_case
        self.expected_path = expected_path
        self.response = response

    async def get(self, request_path):
        self.test_case.assertEqual(self.expected_path, request_path)
        return self.response


class TestAirlyMeasurementsClient(TestCase):
    TEST_INSTALLATION_ID = 7
    EXPECTED_PATH = "measurements/installation?installationId=%d" % \
                    TEST_INSTALLATION_ID

    def create_sut_mocked_with_file(self, file_name):
        with open(file_name) as json_file:
            data = json.load(json_file)
        mock = AirlyRequestsFactoryMock(self, self.EXPECTED_PATH, data)
        self.sut = AirlyMeasurementsClient(
            mock, installation=self.TEST_INSTALLATION_ID)

    def wait_for_update(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.sut.update())
        loop.close()

    def test_get_value_emptyClient(self):
        sut = AirlyMeasurementsClient(
            None, installation=self.TEST_INSTALLATION_ID)

        self.assertIsNone(sut.current.pm1)
        self.assertIsNone(sut.current.pm25)
        self.assertIsNone(sut.current.pm10)
        self.assertIsNone(sut.current.temperature)
        self.assertIsNone(sut.current.humidity)
        self.assertIsNone(sut.current.pressure)
        self.assertIsNone(sut.current.no2)
        self.assertIsNone(sut.current.o3)

    def test_update_correctJson(self):
        self.create_sut_mocked_with_file(
            "test_AirlyMeasurementsClient_Correct.json")

        self.wait_for_update()

        self.assertIsNone(self.sut.current.pm1)
        self.assertEqual(26.6, self.sut.current.pm25)
        self.assertEqual(29.4, self.sut.current.pm10)
        self.assertIsNone(self.sut.current.temperature)
        self.assertIsNone(self.sut.current.humidity)
        self.assertIsNone(self.sut.current.pressure)
        self.assertEqual(46.23, self.sut.current.no2)
        self.assertIsNone(self.sut.current.o3)
