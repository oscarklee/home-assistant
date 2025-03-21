import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
os.chdir(ROOT_DIR)
sys.path.append(ROOT_DIR)

import asyncio
import logging
from custom_components.automation_core.service import AutomationService
from custom_components.automation_core.automations.whatsapp.lib import WhatsApp, WhatsAppEventName
from playwright.async_api import Page

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
LOGGER = logging.getLogger(__name__)

async def main():
    LOGGER.info("Testing WhatsApp Automation")
    automation_service = AutomationService()
    try:
        WhatsApp._event_emitter.add_listener(WhatsAppEventName.NEW_QR_SCREENSHOT, lambda path: LOGGER.info(f"New QR!! : {path}"))
        WhatsApp._event_emitter.add_listener(WhatsAppEventName.LOGIN_STATUS, lambda status: LOGGER.info(f"New Status: {status}"))
        page: Page = await automation_service.get_page('whatsapp')
        await WhatsApp.login(page)
    except Exception as e:
        LOGGER.error(f"Error: {e}")

    try:
        while True:
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        await automation_service.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Program exited")