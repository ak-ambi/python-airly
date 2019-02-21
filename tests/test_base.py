import json
from unittest import TestCase, mock

from airly._private import _RequestsHandler
from utils import wrap_to_future


class AirlyTestCase(TestCase):

    def setUp(self):
        self._rh_mock = mock.create_autospec(_RequestsHandler)

    def set_up_next_response_from_file(self, file_id):
        file_name = "data/{}.json".format(file_id)
        with open(file_name) as file:
            data = json.load(file)
            self._rh_mock.get.side_effect = [wrap_to_future(data)]

    def assert_rh_called_once_with_url(self, expected_url, float_params):
        self.assertEqual(1, self._rh_mock.get.call_count)
        self.assert_url(
            expected_url, self._rh_mock.get.call_args[0][0], float_params)

    def assert_url(self, expected, actual, float_types=()):
        """
        This will compare url with special care for query string params.

        When comparing query strings, values of float type will be compared
        using self.assertAlmostEqual() method.
        :param expected: expected url as string
        :param actual: actual url as string
        :param float_types: List of query string parameters' names that should
        be compared using assertAlmostEqual().
        """
        import urllib
        expected_parts = urllib.parse.urlparse(expected)
        actual_parts = urllib.parse.urlparse(actual)
        self.assertEqual(self._get_parts_wo_qs(expected_parts),
                         self._get_parts_wo_qs(actual_parts))

        expected_qsl = urllib.parse.parse_qs(expected_parts.query)
        actual_qsl = urllib.parse.parse_qs(actual_parts.query)
        self.assertCountEqual(expected_qsl, actual_qsl)
        for k in expected_qsl:
            self.assertIn(k, actual_qsl)
            expected_val = ','.join(expected_qsl[k])
            actual_val = ','.join(actual_qsl[k])
            if k in float_types:
                self.assertAlmostEqual(float(expected_val), float(actual_val))
            else:
                self.assertEqual(expected_val, actual_val)

    @staticmethod
    def _get_parts_wo_qs(parts):
        return parts[:3] + parts[5:]