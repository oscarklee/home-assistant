from dataclasses import dataclass, field
import asyncio
import logging
from typing import Dict, Optional
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from playwright.async_api import Page, async_playwright, ChromiumBrowserContext
from custom_components.automation_core.utils import get_main_domain

DOMAIN = get_main_domain()

logger = logging.getLogger(__name__)

@dataclass
class AutomationService:
    hass: HomeAssistant
    config_entry: ConfigEntry
    user_data_dir: Path = field(default_factory=lambda: Path("./User_Data").absolute())
    pages: Dict[str, Page] = field(default_factory=dict)
    _locks: Dict[str, asyncio.Lock] = field(default_factory=dict)
    _context: Optional[ChromiumBrowserContext] = None
    _shutdown_event: asyncio.Event = field(default_factory=asyncio.Event)

    def __post_init__(self) -> None:
        self.user_data_dir.mkdir(exist_ok=True)
        asyncio.create_task(self._initialize())

    async def _initialize(self) -> None:
        try:
            async with async_playwright() as playwright:
                self._context = await playwright.chromium.launch_persistent_context(
                    user_data_dir=str(self.user_data_dir),
                    headless=False
                )
                await self._shutdown_event.wait()
                await self._cleanup()
        except Exception as e:
            logger.error(f"Automation Core initialization failed: {e}")
            raise

    async def _cleanup(self) -> None:
        if self._context:
            await self._context.close()
            self._context = None
        self.pages.clear()

    async def shutdown(self) -> None:
        self._shutdown_event.set()

    async def get_context(self) -> ChromiumBrowserContext:
        while True:
            if self._context is not None:
                return self._context
            
            await asyncio.sleep(0)

    async def _get_lock(self, page_id: str) -> asyncio.Lock:
        if page_id not in self._locks:
            self._locks[page_id] = asyncio.Lock()
        return self._locks[page_id]

    async def get_page(self, page_id: str) -> Optional[Page]:       
        lock = await self._get_lock(page_id)
        async with lock:
            if page := self.pages.get(page_id):
                return page
            
            context = await asyncio.wait_for(self.get_context(), timeout=10)
            new_page = await context.new_page()
            self.pages[page_id] = new_page
            return new_page