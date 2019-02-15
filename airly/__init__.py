"""
Python wrapper for getting air quality data from Airly sensors.
"""
import json
import logging
from enum import Enum

import aiohttp

_LOGGER = logging.getLogger(__name__)


class AirlyError(Exception):
    """Raised when Airly APi request ended in error.

    Attributes:
        status_code - error code returned by Airly
        status - more detailed description
        """

    def __init__(self, status_code, status):
        self.status_code = status_code
        self.status = status


class _AirlyRequestsHandler:
    """Internal class to create Airly requests"""

    def __init__(self, api_key, base_url, language=None):
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'apikey': api_key,
        }
        if language is not None:
            headers['Accept-Language'] = language
        self.base_url = base_url
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def get(self, request_path):
        url = self.base_url + request_path
        _LOGGER.debug("Sending request: " + url)
        async with self.session.get(url) as response:
            if response.status != 200:
                _LOGGER.warning("Invalid response from Airly API: %s",
                                response.status)
                raise AirlyError(response.status, await response.text())

            return await response.json()


class AirlyMeasurement:
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
            x['name']: x['value'] for x in data['values']} if 'values' in data else {}

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


class _MeasurementByLocationMode(Enum):
    NEAREST_INSTALLATION = 1
    INTERPOLATE = 2


class AirlyMeasurementsClient:
    """A class for polling for measurements from Airly API."""

    _REQUEST_BY_INSTALLATION_FORMAT = \
        "measurements/installation?installationId={:d}"
    _REQUEST_BY_NEAREST_FORMAT = \
        "measurements/nearest?lat={:f}&lng={:f}"
    _REQUEST_BY_INTERPOLATED_FORMAT = "measurements/point?lat={:f}&lng={:f}"

    def __init__(self, requests_handler: _AirlyRequestsHandler, **kwargs):
        """Initialize the connection to specific installation"""
        self.requests_handler = requests_handler
        if 'installation' in kwargs:
            self.request_path = self._REQUEST_BY_INSTALLATION_FORMAT.format(
                kwargs['installation'])
        elif 'latitude' in kwargs and 'longitude' in kwargs:
            lat = kwargs['latitude']
            lng = kwargs['longitude']
            if kwargs.get('mode') == \
                    _MeasurementByLocationMode.NEAREST_INSTALLATION:
                self.request_path = self._REQUEST_BY_NEAREST_FORMAT.format(
                    lat, lng)
                max_distance = kwargs.get('max_distance_km')
                if max_distance is not None:
                    self.request_path += "&maxDistanceKM={:f}"\
                        .format(kwargs['max_distance_km'])
            else:
                self.request_path = self._REQUEST_BY_INTERPOLATED_FORMAT.\
                    format(kwargs['latitude'], kwargs['longitude'])

        self.current = AirlyMeasurement({})
        self.history = []
        self.forecast = []

    async def update(self):
        """Get measurements."""
        data = await self.requests_handler.get(self.request_path)
        _LOGGER.debug(json.dumps(data))
        self.current = AirlyMeasurement(data['current'])
        self.history = [AirlyMeasurement(x) for x in data['history']]
        self.forecast = [AirlyMeasurement(x) for x in data['forecast']]


class AirlyFactory:
    """Main class to perform Airly APi requests"""
    AIRLY_API_URL = "https://airapi.airly.eu/v2/"

    def __init__(self, api_key, base_url=AIRLY_API_URL, language=None):
        self.requests_handler = _AirlyRequestsHandler(
            api_key, base_url, language)

    async def __aenter__(self):
        await self.requests_handler.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.requests_handler.__aexit__(exc_type, exc_val, exc_tb)

    def create_measurements_client_by_installation(self, installation):
        return AirlyMeasurementsClient(
            self.requests_handler, installation=installation)

    def create_measurements_client_by_nearest_installation(
            self, latitude, longitude, max_distance_km=None):
        return AirlyMeasurementsClient(
            self.requests_handler,
            mode=_MeasurementByLocationMode.NEAREST_INSTALLATION,
            latitude=latitude, longitude=longitude,
            max_distance_km=max_distance_km)

    def create_measurements_client_by_interpolated_installation(
            self, latitude, longitude):
        return AirlyMeasurementsClient(
            self.requests_handler,
            mode=_MeasurementByLocationMode.INTERPOLATE,
            latitude=latitude, longitude=longitude)
