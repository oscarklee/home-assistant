from homeassistant.core import HomeAssistant, Event
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from custom_components.automation_core.utils import get_domain

DOMAIN = get_domain(__file__)

class WhatsAppLoginSensor(SensorEntity):
    """Sensor to show WhatsApp login status."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self._config = config_entry.data
        self._attr_name = "WhatsApp Login Status"
        self._attr_unique_id = f"{config_entry.entry_id}_login_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name="WhatsApp",
            model="WhatsApp",
            manufacturer="oklee",
            entry_type=DeviceEntryType.SERVICE,
        )

        self._state = "unknown"
        event_name = f"event.{DOMAIN}_login_status"
        hass.bus.async_listen(event_name, self._handle_event)

    async def _handle_event(self, event: Event):
        """Handle the event."""
        new_state = event.data.get("state")
        if new_state:
            self._state = new_state
            self.async_write_ha_state()
            print(f"Estado actualizado a: {new_state}")

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Update the sensor state."""
        self._state = "unknown"