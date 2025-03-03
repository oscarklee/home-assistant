import logging
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.sensor import State
from custom_components.automation_core.utils import get_domain
from custom_components.automation_core.entity import ButtonAutomationEntity

_LOGGER = logging.getLogger(__name__)

class WhatsAppLoginButton(ButtonAutomationEntity):
    """Button to login to WhatsApp."""
    
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(hass, config_entry)
        self._domain = get_domain(__file__)
        self._attr_name = "WhatsApp Login"
        self._attr_unique_id = f"{config_entry.entry_id}_login_button"
        self._attr_device_info = DeviceInfo(
            identifiers={(self._domain, config_entry.entry_id)},
            name="WhatsApp",
            model="WhatsApp",
            manufacturer="oklee",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_press(self) -> None:
        """Activate the button."""
        sensor: State = self.hass.states.get(f"sensor.{self._domain}_login_status")
        if sensor.state == "logged_in":
            _LOGGER.info("Already logged in")
            return
        
        print("Iniciando sesión en WhatsApp")
        try:
            if self._page:
                await self._page.goto("https://web.whatsapp.com")
        except (asyncio.TimeoutError, Exception) as e:
            print(f"Failed to initialize WhatsApp page: {e}")

        event_name = f"event.{self._domain}_login_status"
        self.hass.bus.fire(event_name, {"state": "logged_in"})