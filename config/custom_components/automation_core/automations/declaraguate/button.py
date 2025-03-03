from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from custom_components.automation_core.utils import get_domain
from custom_components.automation_core.entity import ButtonAutomationEntity

class DeclaraGuateButton(ButtonAutomationEntity):
    """Button to pay taxes in Guatemala."""
    
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(hass, config_entry)
        self._domain = get_domain(__file__)
        self._attr_name = "Declaraguate"
        self._attr_unique_id = f"{config_entry.entry_id}_declaraguate_button"
        self._attr_device_info = DeviceInfo(
            identifiers={(self._domain, config_entry.entry_id)},
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