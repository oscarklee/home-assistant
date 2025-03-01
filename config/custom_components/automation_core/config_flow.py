from typing import Any
from custom_components.automation_core.utils import get_main_domain
from homeassistant.config_entries import(
    ConfigFlow, 
    ConfigFlowResult)

DOMAIN = get_main_domain()

class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""

        await self.async_set_unique_id(DOMAIN)
        if user_input is not None:
            return self.async_create_entry(title="Automation Core", data=user_input)

        return self.async_show_form(step_id="user",errors={})