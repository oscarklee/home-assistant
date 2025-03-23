import logging
import asyncio
import re

from typing import Optional, List, Dict
from pathlib import Path
from custom_components.automation_core import utils
from dataclasses import dataclass
from playwright.async_api import Page, TimeoutError, ElementHandle
from playwright.async_api import expect
from pyee import EventEmitter
from enum import StrEnum
from datetime import datetime, time, timedelta

LOGGER = logging.getLogger(__name__)

class WhatsAppEventName(StrEnum):
    LOGIN_STATUS = "login_status"
    NEW_QR_SCREENSHOT = "new_qr_screenshot"
    MESSAGE_COMING = "message_comming"

class WhatsAppLoginStatus(StrEnum):
    NOT_LOGGED_IN = "not_logged_in"
    LOGGED_IN = "logged_in"
    LOGIN_IN_PROGRESS = "login_in_progress" 

@dataclass
class WhatsAppMessage:
    sender: str
    me: bool
    time: str
    message: str
    unread: bool
    no_of_unread: int
    pattern: str = r"^(1[0-2]|0?[1-9]):([0-5][0-9])\s*(a\.m\.|p\.m\.)$"

    @classmethod
    def from_dict(cls, message_data: dict) -> 'WhatsAppMessage':
        message_data["time"] = cls._parse_time(message_data["time"])
        return cls(**message_data)
    
    @classmethod
    def _parse_time(cls, timeStr: str):
        if (not timeStr):
            return
        
        normalized_str = timeStr.replace("a.m.", "AM").replace("p.m.", "PM")
        if (not re.match(cls.pattern, timeStr)):
            normalized_str = "12:00 AM"

        
        time_obj = datetime.strptime(normalized_str, "%I:%M %p")
        now = datetime.now()
        return time(time_obj.hour, time_obj.minute, now.second, now.microsecond)
    
    def __eq__(self, other):
        if not isinstance(other, WhatsAppMessage):
            return False
        return (self.sender == other.sender and
                self.message == other.message)

class WhatsApp:
    _instance = None
    _lock = asyncio.Lock()
    _state: WhatsAppLoginStatus = WhatsAppLoginStatus.NOT_LOGGED_IN
    event_emitter = EventEmitter()
    _task_queue = asyncio.Queue()
    _worker_task = None
    _shutdown_event: asyncio.Event = asyncio.Event()
    _current_messages: Dict[str, WhatsAppMessage] = {}
    _current_user: str = None

    LANG_PREF = "wa_web_lang_pref"
    BASE_URL = "web.whatsapp.com"
    SUFFIX_LINK = "https://web.whatsapp.com/send?phone={mobile}&text&type=phone_number&app_absent=1"
    QR_PATH = "automation_core/whatsapp/qr.png"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def shutdown(cls):
        cls._shutdown_event.set()
    
    @classmethod
    async def _start_worker(cls):
        if cls._worker_task is None:
            cls._worker_task = asyncio.create_task(cls._worker())

    @classmethod
    async def _worker(cls):
        while not cls._shutdown_event.is_set():
            method, args, kwargs, future = await cls._task_queue.get()
            try:
                result = await method(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                cls._task_queue.task_done()

    @classmethod
    async def create_new_messages_listener_event(cls, page: Page) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._create_new_messages_listener_event, (page,), {}, future))
        return future

    @classmethod
    async def _create_new_messages_listener_event(cls, page: Page):
        async def on_mutation(message_data):
            new_message = WhatsAppMessage.from_dict(message_data)
            message = cls._current_messages.get(new_message.sender)
            if message and new_message.sender == message.sender and (
                new_message.message == message.message or 
                new_message.time < message.time):
                return
            
            cls._current_messages[new_message.sender] = new_message
            cls.event_emitter.emit(WhatsAppEventName.MESSAGE_COMING, new_message)

        await page.expose_function("onMutation", on_mutation)
        pane_side = await page.query_selector('#pane-side')
        await page.evaluate(""" 
        (pane) => {
            const config = { attributes: true, childList: true, subtree: true };
            const callback = function(mutationsList, observer) {
                const listItems = pane.querySelectorAll('div[role="listitem"]');
                const chatItems = Array.from(listItems).filter(item => item.querySelector('span[title]') !== null);
                chatItems.forEach(element => {
                    const messageData = {};
                    const titleElement = element.querySelector('span[title]');
                    messageData.sender = titleElement ? titleElement.getAttribute('title') : 'Unknown';
                    const meElement = titleElement ? titleElement.parentElement.querySelector('span[title] ~ span') : null;
                    messageData.me = !!meElement;
                    const timeElement = element.querySelectorAll('div[role="gridcell"] > div')[1];
                    messageData.time = timeElement ? timeElement.textContent : '';
                    const messageElement = element.querySelector('span[dir="ltr"]');
                    messageData.message = messageElement ? messageElement.textContent : '';
                    const unreadBadge = element.querySelector('span[aria-label*="me"]');
                    messageData.unread = !!unreadBadge;
                    messageData.no_of_unread = 0;
                    if (unreadBadge) {
                        const badgeText = unreadBadge.textContent.trim();
                        messageData.no_of_unread = badgeText && !isNaN(badgeText) ? parseInt(badgeText) : 1;
                    }

                    window.onMutation(messageData);
                });
            };
            
            const observer = new MutationObserver(callback);
            observer.observe(pane, config);
        }
        """, pane_side)
        await cls._shutdown_event.wait()

    @classmethod
    async def is_logged(cls, page: Page) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._is_logged_impl, (page,), {}, future))
        return future

    @classmethod
    async def _is_logged_impl(cls, page: Page) -> bool:
        await cls.go_to_base(page)
        heading_task = asyncio.create_task(page.get_by_role("button", name="Chats").wait_for())
        login_text_task = asyncio.create_task(page.wait_for_selector('text="Log into WhatsApp Web"'))
        done, pending = await asyncio.wait(
            [heading_task, login_text_task],
            return_when=asyncio.FIRST_COMPLETED,
            timeout=30
        )
        for task in pending:
            task.cancel()
        if heading_task in done:
            await heading_task
            return True
        elif login_text_task in done:
            await login_text_task
            return False
        else:
            raise Exception("No se detectó 'heading' ni 'Inicia sesión en WhatsApp Web'.")

    @classmethod
    async def go_to_base(cls, page: Page):
        current_url = page.url
        base_url = f"https://{cls.BASE_URL}/"
        cookies: List[Dict] = await page.context.cookies()
        lang_pref = next((cookie for cookie in cookies if cookie["name"] == cls.LANG_PREF), None)
        if current_url != base_url or (lang_pref and lang_pref["value"] != "en_US"):
            await cls._set_localization(page)
            await page.goto(base_url)

    @classmethod
    async def _set_localization(cls, page:Page):
        await page.context.clear_cookies(name=cls.LANG_PREF)
        await page.context.add_cookies([{
            "name": cls.LANG_PREF,
            "value": "en_US",
            "domain": f".{cls.BASE_URL}",
            "path": "/",
            "secure": True
        }])

    @classmethod
    async def login(cls, page: Page) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._login_impl, (page,), {}, future))
        return future

    @classmethod
    async def _login_impl(cls, page: Page) -> None:
        if cls._state is WhatsAppLoginStatus.LOGIN_IN_PROGRESS:
            LOGGER.info(f"login not executed - current status: {cls._state}")
            return
        if cls._state is WhatsAppLoginStatus.LOGGED_IN or await cls._is_logged_impl(page):
            cls._state = WhatsAppLoginStatus.LOGGED_IN
            cls.event_emitter.emit(WhatsAppEventName.LOGIN_STATUS, cls._state)
        else:
            cls._state = WhatsAppLoginStatus.LOGIN_IN_PROGRESS
            await cls._handle_qr_login(page)
            cls._state = WhatsAppLoginStatus.LOGGED_IN
            cls.event_emitter.emit(WhatsAppEventName.LOGIN_STATUS, cls._state)

    @classmethod
    async def _handle_qr_login(cls, page: Page):
        while not cls._shutdown_event.is_set():
            try:
                if await cls._is_logged_impl(page):
                    break

                qr_selector = page.get_by_role("img", name="Scan this QR code to link a")
                await qr_selector.wait_for(timeout=utils.ONE_SECOND)

                qr_element = await qr_selector.element_handle()
                parent_div: ElementHandle = await qr_element.evaluate_handle("element => element.parentElement")
                current_data_ref = await parent_div.get_attribute("data-ref")

                if current_data_ref != getattr(cls, "_initial_data_ref", None):
                    local_path = f"config/www/{cls.QR_PATH}"
                    remote_path = f"/local/{cls.QR_PATH}"
                    await utils.take_qr_screenshot(qr_selector, local_path)
                    cls.event_emitter.emit(WhatsAppEventName.NEW_QR_SCREENSHOT, remote_path)
                    cls._initial_data_ref = current_data_ref

            except TimeoutError:
                pass

    @classmethod
    async def logout(cls, page: Page) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._logout_impl, (page,), {}, future))
        return future

    @classmethod
    async def _logout_impl(cls, page: Page) -> None:
        settings = page.get_by_role("button", name="Ajustes")
        await settings.click()
        logout_button = page.get_by_role("button", name="Cerrar sesión")
        await logout_button.click()
        confirm_logout = page.get_by_label("¿Deseas cerrar sesión?").get_by_role("button", name="Cerrar sesión")
        await confirm_logout.click()
        LOGGER.info("Sesión cerrada")

    @classmethod
    async def find_by_name(cls, page: Page, name: str) -> asyncio.Future:
        if (cls._current_user == name):
            return

        search_box = page.get_by_role("textbox", name="Search").get_by_role("paragraph")
        await search_box.click()
        await search_box.fill(name)
        await page.get_by_label("Search results.").get_by_role("listitem").get_by_text(name).first.click()
        cls._current_user = name

    @classmethod
    async def find_me(cls, page: Page) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._find_me_impl, (page,), {}, future))
        return future

    @classmethod
    async def _find_me_impl(cls, page: Page) -> None:
        await cls._find_by_name_impl(page, "(Tú)")

    @classmethod
    async def find_user(cls, page: Page, mobile: str) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._find_user_impl, (page, mobile), {}, future))
        return future

    @classmethod
    async def _find_user_impl(cls, page: Page, mobile: str) -> None:
        url = cls.SUFFIX_LINK.format(mobile=mobile)
        await page.goto(url)
        message_input = page.get_by_role("textbox", name="Escribe un mensaje")
        await message_input.wait_for(timeout=utils.minutes(1))

    @classmethod
    async def send_me_message(cls, page: Page, message: str) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._send_me_message_impl, (page, message), {}, future))
        return future

    @classmethod
    async def _send_me_message_impl(cls, page: Page, message: str) -> None:
        await cls._find_me_impl(page)
        await cls._send_message_impl(page, message)

    @classmethod
    async def send_message(cls, page: Page, message: str) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._send_message_impl, (page, message,), {}, future))
        return future

    @classmethod
    async def _send_message_impl(cls, page: Page, message: str) -> None:
        await asyncio.sleep(1)
        if (cls._current_user and cls._current_messages[cls._current_user]):
            current_message: WhatsAppMessage = cls._current_messages[cls._current_user]
            current_message.message = message
            now = datetime.now().time()
            dt = datetime.combine(datetime.today().date(), now)
            dt_plus_5 = dt + timedelta(seconds=5)
            current_message.time = dt_plus_5.time()

        input_box = page.get_by_role("textbox", name="Type a message")
        await input_box.click()
        for line in message.split("\n"):
            await input_box.type(line)
            await page.keyboard.press("Shift+Enter")
        await page.keyboard.press("Enter")

    @classmethod
    async def send_media(cls, page: Page, file_path: Path, message: Optional[str] = None, media_type: str = "image") -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._send_media_impl, (page, file_path), {"message": message, "media_type": media_type}, future))
        return future

    @classmethod
    async def _send_media_impl(cls, page: Page, file_path: Path, message: Optional[str] = None, media_type: str = "image") -> None:
        await page.get_by_role("button", name="Attach").click()
        async with page.expect_file_chooser() as fc_info:
            if media_type == "image":
                await page.get_by_role("button", name="Photos & videos").click()
            elif media_type == "document":
                await page.get_by_role("button", name="Document").click()

            file_chooser = await fc_info.value
            await file_chooser.set_files(file_path)

        if message:
            caption = page.get_by_role("textbox", name="Add a caption")
            await caption.wait_for()
            await caption.type(message)
        await page.get_by_role("button", name="Send", exact=True).click()
        LOGGER.info(f"File {file_path} Sent")

    @classmethod
    async def send_image(cls, page: Page, image_path: Path, caption: Optional[str] = None) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._send_image_impl, (page, image_path), {"caption": caption}, future))
        return future

    @classmethod
    async def _send_image_impl(cls, page: Page, image_path: Path, caption: Optional[str] = None) -> None:
        await cls._send_media_impl(page, image_path, caption, "image")

    @classmethod
    async def send_video(cls, page: Page, video_path: Path, caption: Optional[str] = None) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._send_video_impl, (page, video_path), {"caption": caption}, future))
        return future

    @classmethod
    async def _send_video_impl(cls, page: Page, video_path: Path, caption: Optional[str] = None) -> None:
        await cls._send_media_impl(page, video_path, caption, "video")

    @classmethod
    async def send_document(cls, page: Page, doc_path: Path, caption: Optional[str] = None) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._send_document_impl, (page, doc_path), {"caption": caption}, future))
        return future

    @classmethod
    async def _send_document_impl(cls, page: Page, doc_path: Path, caption: Optional[str] = None) -> None:
        await cls._send_media_impl(page, doc_path, caption, "document")

    @classmethod
    async def send_me_and_wait(cls, page: Page, message: str) -> asyncio.Future:
        await cls._start_worker()
        future = asyncio.Future()
        await cls._task_queue.put((cls._send_me_and_wait_impl, (page, message), {}, future))
        return future

    @classmethod
    async def _send_me_and_wait_impl(cls, page: Page, message: str) -> str:
        await cls._send_me_message_impl(page, message)
        rows = page.get_by_role("application").get_by_role("row")
        chat_current_length = await rows.count()
        await expect(rows).to_have_count(chat_current_length + 1, timeout=utils.minutes(10))
        last_message = rows.last.locator(".selectable-text")
        messages = await last_message.all_text_contents()
        return "".join(messages)