import voluptuous as vol

from typing import Any
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.config_entries import(
    ConfigFlow, 
    ConfigFlowResult, 
    OptionsFlow, 
    ConfigEntry)
from .const import *

class NewsGTFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for news gt integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="News GT", data=user_input)

        data_schema = vol.Schema({
            vol.Required("url", default=URL_DEFAULT): str,
            vol.Required("title", default=TITLE_JSON_PATH): str,
            vol.Required("link", default=LINK_JSON_PATH): str,
            vol.Required("summary", default=SUMMARY_JSON_PATH): str,
            vol.Required("image", default=IMAGE_JSON_PATH): str,
            vol.Required("published", default=PUBLISHED_JSON_PATH): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors={})
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return NewsGTOptionsFlow()
    

class NewsGTOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        options_schema = vol.Schema({
            vol.Required("url", default=self.get_entry("url")): str,
            vol.Required("title", default=self.get_entry("title")): str,
            vol.Required("link", default=self.get_entry("link")): str,
            vol.Required("summary", default=self.get_entry("summary")): str,
            vol.Required("image", default=self.get_entry("image")): str,
            vol.Required("published", default=self.get_entry("published")): str,
        })

        return self.async_show_form(step_id="init", data_schema=options_schema)
    
    def get_entry(self, key: str) -> str:
        return self.config_entry.options.get(key, self.config_entry.data.get(key, ''))