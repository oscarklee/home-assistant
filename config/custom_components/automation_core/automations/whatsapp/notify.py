from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from custom_components.automation_core.entity import NotifyAutomationEntity

class WhatsApp(NotifyAutomationEntity):
    """Implementation of WhatsApp notification service."""

    def __init__(self, hass:HomeAssistant, config_entry: ConfigEntry):
        super().__init__(hass, config_entry)
        self._attr_name = "WhatsApp"
        self._attr_unique_id = f"{config_entry.entry_id}_notify"
        self._attr_device_info = DeviceInfo(
            name="WhatsApp",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(self._domain, config_entry.entry_id)},
            manufacturer="oklee",
            model="WhatsApp",
        )

    async def async_send_message(self, message: str, **kwargs) -> None:
        """Send a message via WhatsApp."""
        # Aquí va la lógica para enviar el mensaje por WhatsApp
        print(f"Enviando mensaje por WhatsApp: {message}")
        # Ejemplo: podrías usar una API externa o una biblioteca
        # await self.hass.async_add_executor_job(send_whatsapp_message, message)