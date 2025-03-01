from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.util.yaml import loader
from typing import List

class EndpointsService():
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self._hass = hass
        self._config_entry = config_entry

    async def get_endpoints(self, call: ServiceCall) -> None:
        """Service to get the attributes of a sensor."""
        result = await self._extract_endpoints('ui-lovelace.yaml')
        return {
            "endpoints": result
        }
    
    async def _extract_endpoints(self, dashboard_path_str: str) -> List[dict]:
        dashboard_path = self._hass.config.path(dashboard_path_str)
        endpoints = []
        with open(dashboard_path, 'r') as file:
            dashboard_config: dict = loader.yaml.load(file, Loader=loader.PythonSafeLoader)
            views: List[dict] = dashboard_config.get('views', [])
            for view in views:
                sections: List[dict] = view.get('sections', [])
                for section in sections:
                    cards: List[dict] = section.get('cards', [])
                    for card in cards:
                        card_keys = card.keys()
                        if 'description' in card_keys and 'entity' in card_keys:
                            endpoints.append({
                                'description': card['description'],
                                'entity': card['entity']
                            })

        return endpoints