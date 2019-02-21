import re
from datetime import datetime
from enum import Enum
import logging
from airly import _private
from airly._private import _EmptyFormat, _DictToObj

_LOGGER = logging.getLogger(__name__)


class Measurement(_DictToObj):
    """Measurement for specific time period returned from Airly API"""

    # Following values are extracted from this API URL:
    # https://airapi.airly.eu/v2/meta/measurements?apikey=
    PM1 = "PM1"
    PM25 = "PM25"
    PM10 = "PM10"
    TEMPERATURE = "TEMPERATURE"
    HUMIDITY = "HUMIDITY"
    PRESSURE = "PRESSURE"
    NO2 = "NO2"
    O3 = "O3"

    MEASUREMENTS_TYPES = [
        PM1,
        PM25,
        PM10,
        TEMPERATURE,
        HUMIDITY,
        PRESSURE,
        NO2,
        O3,
    ]

    def _parse_list(self, key):
        result = []
        list_to_parse = self.get(key)
        if list_to_parse is not None:
            for e in list_to_parse:
                result.append(_DictToObj(e))
        return result

    def __init__(self, data: dict):
        super().__init__(data)

        # Parse date-times
        self.fromDateTime = self._parse_datetime(data.get('fromDateTime'))
        self.tillDateTime = self._parse_datetime(data.get('tillDateTime'))

        # Make popular measurements available directly,
        # i.e. instead of x.values['PM1'] make it accessible as x.pm1
        self.values = {
            x['name']: x['value'] for x in
            data['values']} if 'values' in data else {}
        for t in Measurement.MEASUREMENTS_TYPES:
            self.__setattr__(t.lower(),
                             self.values[t] if t in self.values else None)

        self.indexes = self._parse_list('indexes')
        self.standards = self._parse_list('standards')

    @staticmethod
    def _parse_datetime(x):
        if x is None:
            return None
        # full timestamp with milliseconds
        match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z", x)
        if match:
            return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ")

        # timestamp missing milliseconds
        match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", x)
        if match:
            return datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")


class MeasurementsSession:
    """A class for polling for measurements from Airly API."""

    class Mode(Enum):
        INSTALLATION = 0
        NEAREST = 1
        POINT = 2

    _REQUEST_INSTALLATION_FORMAT = \
        "measurements/installation?installationId={:d}"
    _REQUEST_NEAREST_FORMAT = \
        "measurements/nearest?lat={:f}&lng={:f}&maxDistanceKM={:f}"
    _REQUEST_POINT_FORMAT = "measurements/point?lat={:f}&lng={:f}"

    def __init__(self,
                 requests_handler: _private,
                 mode: Mode,
                 **kwargs):
        """Initialize the connection to specific installation"""
        self.requests_handler = requests_handler
        if mode == self.Mode.INSTALLATION:
            self.request_path = self._REQUEST_INSTALLATION_FORMAT.format(
                kwargs['installation_id'])
        else:
            lat = kwargs['latitude']
            lng = kwargs['longitude']
            if mode == self.Mode.NEAREST:
                dist = kwargs.get('max_distance_km')
                self.request_path = self._REQUEST_NEAREST_FORMAT.format(
                    lat, lng, dist if dist is not None else _EmptyFormat())
            else:
                self.request_path = self._REQUEST_POINT_FORMAT.format(lat, lng)

        self.current = Measurement({})
        self.history = []
        self.forecast = []

    async def update(self):
        """Get measurements."""
        data = await self.requests_handler.get(self.request_path)
        self.current = Measurement(data['current'])
        self.history = [Measurement(x) for x in data['history']]
        self.forecast = [Measurement(x) for x in data['forecast']]
