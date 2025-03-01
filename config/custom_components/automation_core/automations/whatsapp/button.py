import logging

from homeassistant.core import HomeAssistant
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.sensor import State
from custom_components.automation_core.utils import get_domain

DOMAIN = get_domain(__file__)

_LOGGER = logging.getLogger(__name__)

class WhatsAppLoginButton(ButtonEntity):
    """Button to login to WhatsApp."""
    
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self._config = config_entry.data
        self._attr_name = "WhatsApp Login"
        self._attr_unique_id = f"{config_entry.entry_id}_login_button"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name="WhatsApp",
            model="WhatsApp",
            manufacturer="oklee",
            entry_type=DeviceEntryType.SERVICE,
        )

    def press(self):
        """Activate the button."""
        sensor: State = self.hass.states.get(f"sensor.{DOMAIN}_login_status")
        if sensor.state == "logged_in":
            _LOGGER.info("Already logged in")
            return
        
        print("Iniciando sesión en WhatsApp")
        event_name = f"event.{DOMAIN}_login_status"
        self.hass.bus.fire(event_name, {"state": "logged_in"})