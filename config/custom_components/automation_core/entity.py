import inspect
import sys
import os

from homeassistant.components.button import ButtonEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.notify import NotifyEntity
from homeassistant.components.image import ImageEntity
from playwright.async_api import Page

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.automation_core.utils import get_main_domain, get_domain

class AutomationEntity:
    """Entity created to handle Playwright components"""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        args = self._get_init_args(hass, config_entry)
        super().__init__(**args)
        self.hass = hass
        self._config = config_entry.data
        self._domain = get_domain(self._get_file())
        self._page: Page = None

    def _get_init_args(self, hass: HomeAssistant, config_entry: ConfigEntry):
        mro = type(self).__mro__
        current_index = mro.index(AutomationEntity)
        if current_index + 1 >= len(mro):
            return {}
        
        next_class = mro[current_index + 1]
        try:
            sig = inspect.signature(next_class.__init__)
            parameters = sig.parameters
        except AttributeError:
            parameters = {}

        needs_hass = 'hass' in parameters
        needs_config = 'config_entry' in parameters
        filtered_kwargs = {}
        if needs_hass:
            filtered_kwargs['hass'] = hass
        if needs_config:
            filtered_kwargs['config_entry'] = config_entry

        return filtered_kwargs

    def _get_file(self):
        clazz = self.__class__
        module = sys.modules.get(clazz.__module__)
        return module.__file__

    async def async_added_to_hass(self) -> None:
        if self._domain:
            self._page = await self.hass.data[get_main_domain()]['get_page'](self._domain)

class ButtonAutomationEntity(AutomationEntity, ButtonEntity):
    pass

class SensorAutomationEntity(AutomationEntity, SensorEntity):
    pass

class NotifyAutomationEntity(AutomationEntity, NotifyEntity):
    pass

class ImageAutomationEntity(AutomationEntity, ImageEntity):
    pass