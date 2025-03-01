import voluptuous as vol

from typing import Any
from homeassistant.helpers import selector
from homeassistant.config_entries import(
    ConfigFlow, 
    ConfigFlowResult)
from .const import *

class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""

        await self.async_set_unique_id(DOMAIN)
        if user_input is not None:
            return self.async_create_entry(title="Endpoints Exposer", data=user_input)
        
        element_schema = vol.Schema({
            vol.Required("description"): str,
            vol.Required("message"): selector.TextSelector(
                selector.TextSelectorConfig(multiline=True))
        })

        data_schema = vol.Schema({
            vol.Required("elements"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[],
                    multiple=True,
                    custom_value=True,
                    mode=selector.SelectSelectorMode.LIST
                )
            )
        }).extend(element_schema.schema)

        return self.async_show_form(step_id="user",data_schema=data_schema,errors={})