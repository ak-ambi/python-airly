from unittest import TestCase


def wrap_to_future(result):
    import asyncio
    future = asyncio.get_event_loop().create_future()
    if isinstance(result, BaseException):
        future.set_exception(result)
    else:
        future.set_result(result)
    return future


class AirlyTestCase(TestCase):
    @staticmethod
    def get_parts_wo_qs(parts):
        return parts[:3] + parts[5:]

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
        self.assertEqual(self.get_parts_wo_qs(expected_parts),
                         self.get_parts_wo_qs(actual_parts))

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
