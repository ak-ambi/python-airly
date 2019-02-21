from airly import _InstallationsLoader
from test_base import AirlyTestCase
from utils import run_coroutine_synchronously


class InstallationsLoaderTestCase(AirlyTestCase):
    TEST_INSTALLATION_ID = 56

    def assert_rh_called_once_with_url(self, expected_url):
        super().assert_rh_called_once_with_url(expected_url,
                                               ('lat', 'lng', 'maxDistanceKM'))

    def setUp(self):
        super().setUp()
        self.sut = _InstallationsLoader(self._rh_mock)

    def test_load_nearest_empty_response(self):
        self.set_up_next_response_from_file('installations_empty')

        results = run_coroutine_synchronously(
            self.sut.load_nearest(23.45, 34.45))

        self.assert_rh_called_once_with_url(
            "installations/nearest?lat=23.45&lng=34.45")
        self.assertEqual(0, len(results))

    def test_load_nearest_all_args(self):
        self.set_up_next_response_from_file('installations_empty')

        results = run_coroutine_synchronously(
            self.sut.load_nearest(
                23.45, 34.45, max_distance_km=5, max_results=7))

        self.assert_rh_called_once_with_url(
            "installations/nearest?lat=23.45&lng=34.45&maxDistanceKM=5"
            "&maxResults=7")
        self.assertEqual(0, len(results))

    def test_load_by_id_typical_response(self):
        self.set_up_next_response_from_file('installations_typical')

        result = run_coroutine_synchronously(self.sut.load_by_id(204))

        self.assertEqual(204, result.id)

        self.assertAlmostEqual(50.062006, result.location.latitude)
        self.assertAlmostEqual(19.940984, result.location.longitude)

        self.assertEqual('Poland', result.address.country)
        self.assertEqual('Kraków', result.address.city)
        self.assertEqual('Mikołajska', result.address.street)
        self.assertEqual('4B', result.address.number)
        self.assertEqual('Kraków', result.address.displayAddress1)
        self.assertEqual('Mikołajska', result.address.displayAddress2)

        self.assertEqual(204, result.id)
        self.assertEqual(204, result.id)

        self.assertEqual(7, result.sponsor.id)
        self.assertEqual('KrakówOddycha', result.sponsor.name)
        self.assertEqual("Sensor Airly w ramach akcji",
                         result.sponsor.description)
        self.assertEqual("https://cdn.airly.eu/logo/KrakówOddycha.jpg",
                         result.sponsor.logo)
        self.assertEqual("https://przykladowy_link_do_strony_sponsora.pl",
                         result.sponsor.link)
