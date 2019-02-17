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


async def main():
    pyairly_logger = logging.getLogger('pyairly')
    pyairly_logger.setLevel(logging.DEBUG)
    pyairly_logger.addHandler(logging.StreamHandler(sys.stdout))
    async with aiohttp.ClientSession() as http_session:
        airly = Airly(API_KEY, http_session)
        measurements_clients = OrderedDict([
            ('for specific installation',
                airly.create_measurements_session_installation(2764)),
            ('for nearest installation',
                airly.create_measurements_session_nearest(
                    LATITUDE, LONGITUDE)),
            ('interpolated for specific point',
                airly.create_measurements_session_point(
                    LATITUDE, LONGITUDE))
        ])

        for description, client in measurements_clients.items():
            print()
            sys.stdout.flush()
            await client.update()
            sys.stdout.flush()
            current = client.current
            print("Measurements %s:" % description)
            for m in Measurement.MEASUREMENTS_TYPES:
                print("%s: %s" % (m, current.get_value(m)))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
