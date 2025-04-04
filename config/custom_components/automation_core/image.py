from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.image import ImageEntity
from custom_components.automation_core.utils import get_automation_instances_of_type

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add image entities from a config_entry."""
    entities = get_automation_instances_of_type(hass, config_entry, ImageEntity)
    async_add_entities(entities)