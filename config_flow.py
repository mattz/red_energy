Certainly! To support adding the username and password directly via the Home Assistant GUI, we will use Home Assistant's config_flow.py to manage the OAuth authentication and request the token dynamically from the user. This approach will allow you to retrieve the token without needing to manually edit the configuration.yaml file.

Here is the updated code, which adds the necessary flow for handling username and password input via the Home Assistant UI, as well as the logic to retrieve the token from Red Energy.
1. manifest.json

{
  "domain": "red_energy",
  "name": "Red Energy",
  "version": "1.0",
  "requirements": [
    "oauthlib==3.2.0",
    "requests==2.25.1",
    "requests_oauthlib==1.3.0"
  ],
  "config_flow": true,
  "dependencies": [],
  "codeowners": ["@your_github_username"],
  "documentation": "https://www.example.com",
  "iot_class": "cloud_polling"
}

2. __init__.py

This file handles the initialization of the integration and data retrieval.

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

3. config_flow.py

This file handles the OAuth2 flow where users enter their credentials via the UI to authenticate and retrieve the access token.

import logging
import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class RedEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Red Energy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step of the config flow."""
        if user_input is None:
            return self.async_show_form(step_id="user")

        username = user_input["username"]
        password = user_input["password"]

        # Authenticate with Red Energy
        session_token = await self._authenticate(username, password)
        if session_token:
            # Retrieve the access token using the session token
            access_token = await self._get_access_token(session_token)
            if access_token:
                # Successfully authenticated, create the entry and return
                return self.async_create_entry(title="Red Energy", data={"access_token": access_token})
            else:
                return self.async_show_form(step_id="user", errors={"base": "invalid_token"})

        return self.async_show_form(step_id="user", errors={"base": "invalid_credentials"})

    async def _authenticate(self, username, password):
        """Authenticate with Red Energy via Okta to get session token."""
        url = "https://redenergy.okta.com/api/v1/authn"
        headers = {"Content-Type": "application/json"}
        data = {
            "password": password,
            "username": username,
            "options": {
                "warnBeforePasswordExpired": False,
                "multiOptionalFactorEnroll": False
            }
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get("sessionToken")
        else:
            _LOGGER.error("Failed to authenticate with Red Energy")
            return None

    async def _get_access_token(self, session_token):
        """Exchange session token for access token using OAuth2."""
        discovery_url = "https://login.redenergy.com.au/oauth2/default/.well-known/openid-configuration"
        discovery_response = requests.get(discovery_url).json()

        token_url = discovery_response.get("token_endpoint")
        data = {
            "grant_type": "authorization_code",
            "code": session_token,  # Assuming this is an authorization code
            "redirect_uri": "your_redirect_uri",  # Replace with your redirect URI
            "client_id": "your_client_id",  # Replace with your client ID
            "client_secret": "your_client_secret",  # Replace with your client secret
        }

        token_response = requests.post(token_url, data=data)
        if token_response.status_code == 200:
            return token_response.json().get("access_token")
        else:
            _LOGGER.error(f"Failed to get access token: {token_response.status_code}")
            return None
