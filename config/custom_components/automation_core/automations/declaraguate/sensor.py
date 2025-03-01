from homeassistant.core import HomeAssistant, Event
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from custom_components.automation_core.utils import get_domain

DOMAIN = get_domain(__file__)

class DeclaraGuateSensor(SensorEntity):
    """Sensor to show DeclaraGuate status."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self._config = config_entry.data
        self._attr_name = "Declaraguate Status"
        self._attr_unique_id = f"{config_entry.entry_id}_declaraguate_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name="Declaraguate",
            model="Declaraguate",
            manufacturer="oklee",
            entry_type=DeviceEntryType.SERVICE,
        )
        self._state = "unknown"

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Update the sensor state."""
        self._state = "paid"