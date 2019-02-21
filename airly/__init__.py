"""
Python wrapper for getting air quality data from Airly sensors.
"""
import logging

import aiohttp

from airly.installations import _InstallationsLoader
from airly.measurements import MeasurementsSession

_LOGGER = logging.getLogger(__name__)


class Airly:
    """Main class to perform Airly APi requests"""
    AIRLY_API_URL = "https://airapi.airly.eu/v2/"

    def __init__(self, api_key, session: aiohttp.ClientSession,
                 base_url=AIRLY_API_URL, language=None):
        from airly._private import _RequestsHandler
        self._rh = _RequestsHandler(api_key, session, base_url, language)
        self._installations = _InstallationsLoader(self._rh)

    def load_installation_by_id(self, installation_id):
        return self._installations.load_by_id(installation_id)

    def load_installation_nearest(self, latitude, longitude,
                                  max_distance_km=None, max_results=None):
        return self._installations.load_nearest(
            latitude, longitude,
            max_distance_km=max_distance_km, max_results=max_results)

    def create_measurements_session_installation(self, installation_id):
        return MeasurementsSession(
            self._rh, MeasurementsSession.Mode.INSTALLATION,
            installation_id=installation_id)

    def create_measurements_session_nearest(
            self, latitude, longitude, max_distance_km=None):
        return MeasurementsSession(
            self._rh,
            MeasurementsSession.Mode.NEAREST,
            latitude=latitude, longitude=longitude,
            max_distance_km=max_distance_km)

    def create_measurements_session_point(
            self, latitude, longitude):
        return MeasurementsSession(
            self._rh, MeasurementsSession.Mode.POINT,
            latitude=latitude, longitude=longitude)
