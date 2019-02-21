from airly._private import _EmptyFormat, _DictToObj


class Installation(_DictToObj):
    @property
    def location(self):
        return _DictToObj(self.get('location'))

    @property
    def address(self):
        return _DictToObj(self.get('address'))

    @property
    def sponsor(self):
        return _DictToObj(self.get('sponsor'))


class _InstallationsLoader:
    def __init__(self, requests_handler):
        self._rh = requests_handler

    _REQUEST_BY_ID_FORMAT = "installations/{:d}"
    _REQUEST_NEAREST_FORMAT = "installations/nearest?lat={:f}&lng={:f}" \
                              "&maxDistanceKM={:f}&maxResults={:d}"

    async def load_by_id(self, installation_id):
        data = await self._load(
            self._REQUEST_BY_ID_FORMAT.format(installation_id))
        return Installation(data)

    async def load_nearest(self, latitude, longitude,
                           max_distance_km=None, max_results=None):
        if max_distance_km is None:
            max_distance_km = _EmptyFormat()
        if max_results is None:
            max_results = _EmptyFormat()
        data = await self._load(self._REQUEST_NEAREST_FORMAT.format(
            latitude, longitude, max_distance_km, max_results))
        return [Installation(x) for x in data]

    def _load(self, request_path):
        return self._rh.get(request_path)
