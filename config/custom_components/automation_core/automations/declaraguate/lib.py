import logging

from playwright.async_api import Page
from custom_components.automation_core import utils
from custom_components.automation_core.automations.whatsapp.lib import WhatsApp, WhatsAppEventName, WhatsAppMessage, WhatsAppLoginStatus

LOGGER = logging.getLogger(__name__)

class DeclaraGuate:
    _instance = None
    _page: Page = None

    BASE_URL = "declaraguate.sat.gob.gt/declaraguate-web/catalogo.iface"
    CAPTCHA_PATH = "automation_core/declaraguate/captcha.png"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def go_to_base(cls):
        current_url = cls._page.url
        base_url = f"https://{cls.BASE_URL}"
        if current_url != base_url:
            await cls._page.goto(base_url)

    @classmethod
    async def login(cls, page: Page):
        cls._page = page
        async def login_callback(status: WhatsAppLoginStatus):
            if not WhatsAppLoginStatus.LOGGED_IN is status:
                return
            
            WhatsApp.event_emitter.remove_listener(WhatsAppEventName.LOGIN_STATUS, login_callback)
            await cls._login()
        WhatsApp.event_emitter.add_listener(WhatsAppEventName.LOGIN_STATUS, login_callback)

    @classmethod
    async def _login(cls):
        await cls.go_to_base()
        await cls._page.get_by_role("link", name="IVA PEQUEÑO CONTRIBUYENTE").click()
        
        captcha_panel = cls._page.locator("#mainForm\\:captchaPanel")
        captcha_img = captcha_panel.locator("img.iceGphImg")
        local_path = f"config/www/{cls.CAPTCHA_PATH}"
        await utils.take_qr_screenshot(captcha_img, local_path)
        
        WhatsApp.event_emitter.add_listener(WhatsAppEventName.MESSAGE_COMING, lambda event: cls._captcha_resolution(event))
        await WhatsApp.find_by_name("Oscar Klee")
        await WhatsApp._send_image_impl(local_path, "Declaraguate captcha resolution requirement.")

    @classmethod
    async def _captcha_resolution(cls, event: WhatsAppMessage):
        if (event.me):
            LOGGER.info(f"New Message from:{event.sender} message:{event.message}")