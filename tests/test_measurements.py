from datetime import datetime

from airly import MeasurementsSession

from test_base import AirlyTestCase
from utils import run_coroutine_synchronously


class MeasurementsSessionTestCase(AirlyTestCase):
    TEST_INSTALLATION_ID = 7

    def create_default_sut(self):
        return MeasurementsSession(
            self._rh_mock, MeasurementsSession.Mode.INSTALLATION,
            installation_id=self.TEST_INSTALLATION_ID)

    def assert_rh_called_once_with_url(self, expected_url):
        super().assert_rh_called_once_with_url(expected_url,
                                               ('lat', 'lng', 'maxDistanceKM'))

    @staticmethod
    def wait_for_update(sut):
        run_coroutine_synchronously(sut.update())

    def setUp(self):
        super().setUp()
        self.set_up_next_response_from_file('measurements_empty')

    def test_get_value_on_initial_object(self):
        sut = self.create_default_sut()
        cur = sut.current

        # test times
        self.assertIsNone(cur.fromDateTime)
        self.assertIsNone(cur.tillDateTime)

        # test values
        self.assertIsNone(cur.pm1)
        self.assertIsNone(cur.pm25)
        self.assertIsNone(cur.pm10)
        self.assertIsNone(cur.temperature)
        self.assertIsNone(cur.humidity)
        self.assertIsNone(cur.pressure)
        self.assertIsNone(cur.no2)
        self.assertIsNone(cur.o3)
        self.assertIsNone(cur.values.get('nonexistent_measurement'))

    def test_get_value_typical_json(self):
        self.set_up_next_response_from_file('measurements_typical')
        sut = self.create_default_sut()

        self.wait_for_update(sut)
        cur = sut.current

        # test times
        self.assertEqual(datetime(2019, 2, 13, hour=21), cur.fromDateTime)
        self.assertEqual(datetime(2019, 2, 13, hour=22), cur.tillDateTime)

        # test values
        self.assertIsNone(cur.pm1)
        self.assertEqual(26.6, cur.pm25)
        self.assertEqual(29.4, cur.pm10)
        self.assertIsNone(cur.temperature)
        self.assertIsNone(cur.humidity)
        self.assertIsNone(cur.pressure)
        self.assertEqual(46.23, cur.no2)
        self.assertIsNone(cur.o3)

        index = cur.indexes[0]
        self.assertEqual('CAQI', index.name)
        self.assertEqual(44.33, index.value)
        self.assertEqual('LOW', index.level)
        self.assertEqual('Air is quite good.', index.description)
        self.assertEqual('Good day for outdoor activities', index.advice)
        self.assertEqual('#B9CE45', index.color)

        pm25_standard = cur.standards[0]
        self.assertEqual('WHO', pm25_standard.name)
        self.assertEqual('PM25', pm25_standard.pollutant)
        self.assertEqual(25.0, pm25_standard.limit)
        self.assertEqual(106.4, pm25_standard.percent)

        pm10_standard = cur.standards[1]
        self.assertEqual('WHO', pm10_standard.name)
        self.assertEqual('PM10', pm10_standard.pollutant)
        self.assertEqual(50.0, pm10_standard.limit)
        self.assertEqual(58.8, pm10_standard.percent)

        # History & Forecast lists have the same format,
        #   so we do not test parsing of them.
        # Let's only ensure that basic values are correct

        # History
        self.assertEqual(24, len(sut.history))
        last_from_date = datetime(2019, 2, 13, hour=22)
        for e in reversed(sut.history):
            self.assertEqual(last_from_date, e.tillDateTime)
            last_from_date = e.fromDateTime

        # Forecast
        self.assertEqual(24, len(sut.forecast))
        last_till_date = datetime(2019, 2, 13, hour=22)
        for e in sut.forecast:
            self.assertEqual(last_till_date, e.fromDateTime)
            last_till_date = e.tillDateTime

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
