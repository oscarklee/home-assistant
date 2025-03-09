""" Automation Core """

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers import device_registry as dr
from custom_components.automation_core.service import AutomationService
from custom_components.automation_core.utils import get_main_domain

DOMAIN = get_main_domain()
PLATFORMS = [Platform.NOTIFY, Platform.SENSOR, Platform.BUTTON, Platform.IMAGE]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up from config flow."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = config_entry

    automation_service = AutomationService()
    hass.data[DOMAIN]['get_page'] = automation_service.get_page

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    await cleanup_old_device(hass)
    return True

async def cleanup_old_device(hass: HomeAssistant) -> None:
    """Cleanup device without proper device identifier."""
    device_reg = dr.async_get(hass)
    device = device_reg.async_get_device(identifiers={(DOMAIN,)})
    if device:
        _LOGGER.debug("Removing improper device %s", device.name)
        device_reg.async_remove_device(device.id)