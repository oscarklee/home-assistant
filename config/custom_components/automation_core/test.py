import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
os.chdir(ROOT_DIR)
sys.path.append(ROOT_DIR)

import asyncio
import logging
from custom_components.automation_core.service import AutomationService
from custom_components.automation_core.automations.whatsapp.lib import WhatsApp, WhatsAppEventName, WhatsAppLoginStatus, WhatsAppMessage
from playwright.async_api import Page

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
LOGGER = logging.getLogger(__name__)

async def on_login(page: Page, status: WhatsAppLoginStatus):
    LOGGER.info(f"New Status: {status}")
    if WhatsAppLoginStatus.LOGGED_IN is status:
        await WhatsApp.create_new_messages_listener_event(page)

async def forward_message(page: Page, event: WhatsAppMessage):
    LOGGER.info(f"New Message from:{event.sender} message:{event.message}")
    if (event.me):
        await WhatsApp.find_by_name(page, event.sender)
        await WhatsApp._send_image_impl(page, "config/www/automation_core/whatsapp/qr.png", "test message")

async def main():
    LOGGER.info("Testing WhatsApp Automation")
    automation_service = AutomationService()
    try:
        page: Page = await automation_service.get_page('whatsapp')
        WhatsApp.event_emitter.add_listener(WhatsAppEventName.NEW_QR_SCREENSHOT, lambda path: LOGGER.info(f"New QR!! : {path}"))
        WhatsApp.event_emitter.add_listener(WhatsAppEventName.LOGIN_STATUS, lambda status: asyncio.create_task(on_login(page, status)))
        WhatsApp.event_emitter.add_listener(WhatsAppEventName.MESSAGE_COMING, lambda event: asyncio.create_task(forward_message(page, event)))
        await WhatsApp.login(page)
    except Exception as e:
        LOGGER.error(f"Error: {e}")

    try:
        while True:
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        await WhatsApp.shutdown()
        await automation_service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())