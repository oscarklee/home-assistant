"""The News Guatemala integration."""

from __future__ import annotations
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize the News GT"""

    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}
        )
    )

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the News GT from config flow."""

    await _register_custom_card(hass)
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the News GT integration."""

    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    return True

async def _register_custom_card(hass: HomeAssistant):
    """Register the custom Lovelace card."""
    add_extra_js_url(hass, "/local/news_gt/news_gt.js")
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            url_path="/local/news_gt/news_gt.js",
            path=hass.config.path("www/news_gt/news_gt.js")
        )
    ])