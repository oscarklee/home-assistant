import requests
import datetime

from jsonpath import jsonpath
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the News API sensor from a config entry."""

    news_sensor = NewsSensor(hass, entry)
    async_add_entities([news_sensor])

class NewsSensor(SensorEntity):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._url = self.get_entry(entry, "url")
        self._title = self.get_entry(entry, "title")
        self._link = self.get_entry(entry, "link")
        self._summary = self.get_entry(entry, "summary")
        self._image = self.get_entry(entry, "image")
        self._published = self.get_entry(entry, "published")
        self._state = None
        self._attributes = {}
        self._attr_unique_id = "news_gt_sensor"
        self._attr_name = "Latest News"
        self._attr_should_poll = False
        self._hass = hass
        self._unsub_update = async_track_time_interval(self._hass, self.async_update, datetime.timedelta(hours=24))
        hass.async_create_task(self.async_update())

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes
    
    async def async_will_remove_from_hass(self):
        """Cancel the scheduled update."""
        if self._unsub_update:
            self._unsub_update()

    async def async_update(self, now=None):
        response = await self._hass.async_add_executor_job(requests.get, self._url)
        if response.status_code == 200:
            data = response.json()
            self._state = datetime.datetime.now().isoformat()
            articles = []

            titles = self.get_values(data, self._title)
            links = self.get_values(data, self._link)
            summaries = self.get_values(data, self._summary)
            thumbnails = self.get_values(data, self._image)
            published = self.get_values(data, self._published)
            for i in range(max(len(titles), len(summaries), len(thumbnails), len(links), len(published))):
                article = {}
                if i < len(titles):
                    article['title'] = titles[i]
                if i < len(summaries):
                    article['summary'] = summaries[i]
                if i < len(thumbnails):
                    article['thumbnail'] = thumbnails[i]
                if i < len(links):
                    article['link'] = links[i]
                if i < len(published):
                    article['published'] = published[i]
                articles.append(article)

            self._attributes = {'articles': articles}
        else:
            self._state = "Error fetching news"
            self._attributes = {'articles': []}

        self.async_write_ha_state()

    def get_entry(self, entry: ConfigEntry, key: str) -> str:
        return entry.options.get(key, entry.data.get(key, '')) 

    def get_values(self, data: dict, path: str) -> list:
        matches = jsonpath(data, path)
        if matches is False:
            return []
        
        return matches
    