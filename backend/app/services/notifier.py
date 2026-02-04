from app.services.settings_service import SettingsService
from app.db.session import AsyncSessionLocal
import aiohttp
import logging
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
from typing import Optional

logger = logging.getLogger(__name__)

class BaseNotifier:
    async def send_markdown(self, title: str, content: str):
        raise NotImplementedError

class DingTalkNotifier(BaseNotifier):
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def get_config(self) -> tuple[Optional[str], Optional[str]]:
        async with AsyncSessionLocal() as db:
            url_setting = await SettingsService.get_setting(db, "dingtalk_webhook_url")
            secret_setting = await SettingsService.get_setting(db, "dingtalk_secret")
            
            url = url_setting.value if url_setting else None
            secret = secret_setting.value if secret_setting else None
            return url, secret

    async def send_markdown(self, title: str, content: str):
        logger.info(f"Attempting to send DingTalk notification: {title}")
        webhook_url, secret = await self.get_config()
        logger.info(f"DingTalk Config: URL={'Set' if webhook_url else 'Unset'}, Secret={'Set' if secret else 'Unset'}")
        
        if not webhook_url:
            logger.warning("DingTalk Webhook URL not configured. Skipping notification.")
            return

        # Add Signature if Secret exists
        final_url = webhook_url
        if secret:
            timestamp = str(round(time.time() * 1000))
            secret_enc = secret.encode('utf-8')
            string_to_sign = '{}\n{}'.format(timestamp, secret)
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            
            # Check if URL already has params
            separator = "&" if "?" in webhook_url else "?"
            final_url = f"{webhook_url}{separator}timestamp={timestamp}&sign={sign}"

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            }
        }

        try:
            async with self.session.post(final_url, json=payload) as resp:
                if resp.status == 200:
                    res_data = await resp.json()
                    if res_data.get("errcode") == 0:
                        logger.info(f"DingTalk notification sent: {title}")
                    else:
                        logger.error(f"DingTalk error: {res_data}")
                else:
                    logger.error(f"DingTalk HTTP error: {resp.status}")
        except Exception as e:
            logger.error(f"Failed to send DingTalk notification: {e}")

    async def close(self):
        await self.session.close()

# Singleton
notifier = DingTalkNotifier()
