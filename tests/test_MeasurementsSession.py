import asyncio
import json
from unittest import mock

from airly import MeasurementsSession
from airly._private import _RequestsHandler
from utils import AirlyTestCase, wrap_to_future


class MeasurementsSessionTestCase(AirlyTestCase):
    TEST_INSTALLATION_ID = 7

    def create_default_sut(self):
        return MeasurementsSession(
            self._rh_mock, MeasurementsSession.Mode.INSTALLATION,
            installation_id=self.TEST_INSTALLATION_ID)

    def set_up_next_response_from_file(self, file_id):
        file_name = "data/{}.json".format(file_id)
        with open(file_name) as file:
            data = json.load(file)
            self._rh_mock.get.side_effect = [wrap_to_future(data)]

    @staticmethod
    def wait_for_update(sut):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(sut.update())
        loop.close()

    def assert_rh_called_once_with_url(self, expected_url):
        self.assertEqual(1, self._rh_mock.get.call_count)
        float_params = ('lat', 'lng', 'maxDistanceKM')
        self.assert_url(
            expected_url, self._rh_mock.get.call_args[0][0], float_params)

    def setUp(self):
        self._rh_mock = mock.create_autospec(_RequestsHandler)
        self.set_up_next_response_from_file('measurements_empty')

    def test_get_value_on_initial_object(self):
        sut = self.create_default_sut()

        self.assertIsNone(sut.current.pm1)
        self.assertIsNone(sut.current.pm25)
        self.assertIsNone(sut.current.pm10)
        self.assertIsNone(sut.current.temperature)
        self.assertIsNone(sut.current.humidity)
        self.assertIsNone(sut.current.pressure)
        self.assertIsNone(sut.current.no2)
        self.assertIsNone(sut.current.o3)
        self.assertIsNone(sut.current.get_value('nonexistent_measurement'))

    def test_get_value_typical_json(self):
        self.set_up_next_response_from_file('measurements_typical')
        sut = self.create_default_sut()

        self.wait_for_update(sut)

        self.assertIsNone(sut.current.pm1)
        self.assertEqual(26.6, sut.current.pm25)
        self.assertEqual(29.4, sut.current.pm10)
        self.assertIsNone(sut.current.temperature)
        self.assertIsNone(sut.current.humidity)
        self.assertIsNone(sut.current.pressure)
        self.assertEqual(46.23, sut.current.no2)
        self.assertIsNone(sut.current.o3)

    def test_update_installation_mode(self):
        sut = MeasurementsSession(
            self._rh_mock, MeasurementsSession.Mode.INSTALLATION,
            installation_id=23456)

        self.wait_for_update(sut)
        self.assert_rh_called_once_with_url(
            'measurements/installation?installationId=23456')

    def test_update_nearest_mode_default_max_dist(self):
        sut = MeasurementsSession(
            self._rh_mock, MeasurementsSession.Mode.NEAREST,
            latitude=12.567, longitude=345.678)

        self.wait_for_update(sut)
        self.assert_rh_called_once_with_url(
            'measurements/nearest?lat=12.567&lng=345.678')

    def test_update_nearest_mode_max_dist_set(self):
        sut = MeasurementsSession(
            self._rh_mock, MeasurementsSession.Mode.NEAREST,
            latitude=12.567, longitude=345.678, max_distance_km=5.3)

        self.wait_for_update(sut)
        self.assert_rh_called_once_with_url(
            'measurements/nearest?lat=12.567&lng=345.678&maxDistanceKM=5.3')

    def test_update_point_mode(self):
        sut = MeasurementsSession(
            self._rh_mock, MeasurementsSession.Mode.POINT,
            latitude=13.456, longitude=12.345)

        self.wait_for_update(sut)
        self.assert_rh_called_once_with_url(
            'measurements/point?lat=13.456&lng=12.345')
