import logging
import requests
from homeassistant.helpers import config_entry
from homeassistant.components import sensor
from .sensor import create_red_energy_sensors

_LOGGER = logging.getLogger(__name__)

DOMAIN = "red_energy"

def setup(hass, config):
    """Set up the Red Energy integration."""
    return True

async def async_setup_entry(hass, entry):
    """Set up Red Energy from a config entry."""
    access_token = entry.data["access_token"]
    # Fetch user data from Red Energy API
    data = await get_red_energy_data(access_token)

    # Create sensors from the API response
    sensors = create_red_energy_sensors(data)

    # Add the sensors to Home Assistant
    platform = sensor.async_get_platform(hass, "sensor")
    for sensor_entity in sensors:
        platform.async_add_entities([sensor_entity])

    hass.data[DOMAIN] = data  # Store the data if needed
    return True

async def get_red_energy_data(access_token):
    """Fetch data from Red Energy API."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://selfservice.services.retail.energy/v1/customers/current"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        _LOGGER.error(f"Failed to retrieve data: {response.status_code}")
        return {}
