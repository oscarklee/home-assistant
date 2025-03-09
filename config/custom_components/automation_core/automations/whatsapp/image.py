import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from custom_components.automation_core.entity import ImageAutomationEntity
from custom_components.automation_core.automations.whatsapp.lib import WhatsApp, WhatsAppEventName
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class WhatsAppQRImage(ImageAutomationEntity):
    LOCAL_PATH = "/local/automation_core/whatsapp"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(hass, config_entry)
        use_ssl = hass.config.api.use_ssl
        scheme = "https" if use_ssl else "http"
        host = hass.config.api.local_ip
        port = hass.config.api.port
        self._base_url = f"{scheme}://{host}:{port}"
        self._attr_name = "WhatsApp QR Login"
        self._attr_unique_id = f"{config_entry.entry_id}_login_qr_image"
        self._image_path = None
        self._cached_image = None
        self.name = "QR Image"
        self.image_last_updated = datetime.now()
        self._attr_device_info = DeviceInfo(
            identifiers={(self._domain, config_entry.entry_id)},
            name="WhatsApp",
            model="WhatsApp",
            manufacturer="oklee",
            entry_type=DeviceEntryType.SERVICE,
        )
        WhatsApp._event_emitter.on(WhatsAppEventName.NEW_QR_SCREENSHOT, self._handle_new_qr)
    
    @property
    def state(self):
        return self.image_last_updated.strftime("%Y-%m-%d %H:%M:%S")

    def _handle_new_qr(self, path: str):
        now = datetime.now()
        self._image_path = f"{self._base_url}{path}?v={now.timestamp()}"
        self.image_last_updated = now
        self.async_schedule_update_ha_state(True)

    async def async_image(self) -> bytes:
        try:
            if self._image_path is None:
                image_url = f"{self._base_url}{self.LOCAL_PATH}/unknown.png"
            else:
                image_url = self._image_path

            image = await self._async_load_image_from_url(image_url)
            return image.content
        except Exception as e:
            _LOGGER.error(f"Error fetching image: {str(e)}")
            return b""