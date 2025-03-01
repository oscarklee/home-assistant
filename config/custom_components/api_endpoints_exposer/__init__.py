"""API Exposer integration."""

from __future__ import annotations
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.service import SupportsResponse

from .const import DOMAIN
from .service import EndpointsService

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize the Setup"""
    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}
        )
    )
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up from config flow."""
    service = EndpointsService(hass, config_entry)
    hass.services.async_register(
        DOMAIN,
        "get_endpoints",
        service.get_endpoints,
        supports_response=SupportsResponse.ONLY
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    hass.services.async_remove(DOMAIN, "get_sensor_attributes")
    return True
