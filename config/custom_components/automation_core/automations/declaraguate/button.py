from homeassistant.core import HomeAssistant
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from custom_components.automation_core.utils import get_domain

DOMAIN = get_domain(__file__)

class DeclaraGuateButton(ButtonEntity):
    """Button to pay taxes in Guatemala."""
    
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self._config = config_entry.data
        self._attr_name = "Declaraguate"
        self._attr_unique_id = f"{config_entry.entry_id}_declaraguate_button"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name="Declaraguate",
            model="DeclaraGuate",
            manufacturer="oklee",
            entry_type=DeviceEntryType.SERVICE,
        )

    def press(self):
        """Activate the button."""
        # Aquí va la lógica para pagar impuestos
        print("Pagando impuestos")
        # Ejemplo: podrías usar una API externa o una biblioteca
        # await self.hass.async_add_executor_job(pay_taxes)