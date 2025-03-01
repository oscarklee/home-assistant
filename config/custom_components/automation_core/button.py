from homeassistant.core import HomeAssistant
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from custom_components.automation_core.utils import get_automation_instances_of_type

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add button entities from a config_entry."""
    entities = get_automation_instances_of_type(hass, config_entry, ButtonEntity)
    async_add_entities(entities)