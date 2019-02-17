import json
from enum import Enum
import logging
from airly import _private
from airly._private import _EmptyFormat

_LOGGER = logging.getLogger(__name__)


class Measurement:
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

    def __init__(self, data: dict):
        self.values = {
            x['name']: x['value'] for x in
            data['values']} if 'values' in data else {}

    def get_value(self, name):
        return self.values[name] if name in self.values else None

    @property
    def pm1(self):
        return self.get_value(self.PM1)

    @property
    def pm25(self):
        return self.get_value(self.PM25)

    @property
    def pm10(self):
        return self.get_value(self.PM10)

    @property
    def temperature(self):
        return self.get_value(self.TEMPERATURE)

    @property
    def humidity(self):
        return self.get_value(self.HUMIDITY)

    @property
    def pressure(self):
        return self.get_value(self.PRESSURE)

    @property
    def no2(self):
        return self.get_value(self.NO2)

    @property
    def o3(self):
        return self.get_value(self.O3)


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
        _LOGGER.debug(json.dumps(data))
        self.current = Measurement(data['current'])
        self.history = [Measurement(x) for x in data['history']]
        self.forecast = [Measurement(x) for x in data['forecast']]
