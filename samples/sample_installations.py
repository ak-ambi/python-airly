import logging
import sys
from collections import OrderedDict
import asyncio
from pathlib import Path

import aiohttp

from airly import Airly
from airly.measurements import Measurement

# Before running the sample,
#   you need to create .api_key file filled with your API key.
# After you are logged in, you can copy it from here:
#   https://developer.airly.eu/api
try:
    API_KEY = Path('.api_key').read_text()
except FileNotFoundError:
    print('Save your API key in samples/.api_key file', file=sys.stderr)
    exit(1)

INSTALLATION_ID = 204
LATITUDE = 50.06298
LONGITUDE = 19.93534
MAX_DIST_KM = 0.5


async def main():
    pyairly_logger = logging.getLogger('pyairly')
    pyairly_logger.setLevel(logging.DEBUG)
    pyairly_logger.addHandler(logging.StreamHandler(sys.stdout))
    async with aiohttp.ClientSession() as http_session:
        airly = Airly(API_KEY, http_session)

        print('Installation %d:' % INSTALLATION_ID)
        sys.stdout.flush()
        installation = await airly.load_installation_by_id(INSTALLATION_ID)
        sys.stdout.flush()
        print("{}, {}.\n{}: {}".format(installation.address.displayAddress1,
                                       installation.address.displayAddress2,
                                       installation.sponsor.description,
                                       installation.sponsor.name))

        print('\nInstallations {:.2f} km apart from latitude {:f} and '
              'longitude {:f}:\n'
              .format(MAX_DIST_KM, LATITUDE, LONGITUDE))
        sys.stdout.flush()
        installations_list = await airly.load_installation_nearest(
            LATITUDE, LONGITUDE, max_distance_km=MAX_DIST_KM, max_results=-1)
        sys.stdout.flush()
        for i in installations_list:
            print("{}, {}.\n{}: {}\n".format(
                i.address.displayAddress1, i.address.displayAddress2,
                i.sponsor.description, i.sponsor.name))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
