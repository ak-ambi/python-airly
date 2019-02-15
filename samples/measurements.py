import logging
import sys
from collections import OrderedDict
import asyncio

from airly import AirlyFactory, AirlyMeasurement

API_KEY = "<API_KEY>"
INSTALLATION_ID = 204
LATITUDE = 50.06298
LONGITUDE = 19.93534


async def main():
    pyairly_logger = logging.getLogger('pyairly')
    pyairly_logger.setLevel(logging.DEBUG)
    pyairly_logger.addHandler(logging.StreamHandler(sys.stdout))
    async with AirlyFactory(API_KEY) as airly:
        measurements_clients = OrderedDict([
            ('for specific installation',
                airly.create_measurements_client_by_installation(2764)),
            ('for nearest installation',
            airly.create_measurements_client_by_nearest_installation(
                LATITUDE, LONGITUDE)),
            ('interpolated for specific point',
            airly.create_measurements_client_by_interpolated_installation(
                LATITUDE, LONGITUDE))
        ])

        for description, client in measurements_clients.items():
            print()
            sys.stdout.flush()
            await client.update()
            sys.stdout.flush()
            current = client.current
            print("Measurements %s:" % description)
            for m in AirlyMeasurement.MEASUREMENTS_TYPES:
                print("%s: %s" % (m, current.get_value(m)))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
