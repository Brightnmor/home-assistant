"""
Support for the GPSLogger platform.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/device_tracker.gpslogger/
"""
import asyncio
from functools import partial
import logging

from homeassistant.const import HTTP_UNPROCESSABLE_ENTITY
from homeassistant.components.http import HomeAssistantView
# pylint: disable=unused-import
from homeassistant.components.device_tracker import (  # NOQA
    DOMAIN, PLATFORM_SCHEMA)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['http']


def setup_scanner(hass, config, see):
    """Setup an endpoint for the GPSLogger application."""
    hass.http.register_view(GPSLoggerView(hass, see))

    return True


class GPSLoggerView(HomeAssistantView):
    """View to handle gpslogger requests."""

    url = '/api/gpslogger'
    name = 'api:gpslogger'

    def __init__(self, hass, see):
        """Initialize GPSLogger url endpoints."""
        super().__init__(hass)
        self.see = see

    @asyncio.coroutine
    def get(self, request):
        """A GPSLogger message received as GET."""
        res = yield from self._handle(request.GET)
        return res

    @asyncio.coroutine
    # pylint: disable=too-many-return-statements
    def _handle(self, data):
        """Handle gpslogger request."""
        if 'latitude' not in data or 'longitude' not in data:
            return ('Latitude and longitude not specified.',
                    HTTP_UNPROCESSABLE_ENTITY)

        if 'device' not in data:
            _LOGGER.error('Device id not specified.')
            return ('Device id not specified.',
                    HTTP_UNPROCESSABLE_ENTITY)

        device = data['device'].replace('-', '')
        gps_location = (data['latitude'], data['longitude'])
        accuracy = 200
        battery = -1

        if 'accuracy' in data:
            accuracy = int(float(data['accuracy']))
        if 'battery' in data:
            battery = float(data['battery'])

        yield from self.hass.loop.run_in_executor(
            None, partial(self.see, dev_id=device,
                          gps=gps_location, battery=battery,
                          gps_accuracy=accuracy))

        return 'Setting location for {}'.format(device)
