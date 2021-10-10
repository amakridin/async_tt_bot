import asyncio
import json
import logging
from urllib.parse import urljoin

import aiohttp

import config
from errors import DownstreamServiceError

logging.basicConfig(filename="bot.log", level=logging.INFO)


class BaseApiTamTam:
    async def check_errors(self, response):
        response_status = response.status
        if response_status < 200:
            return
        if response_status >= 400:
            error_message: str
            err = await response.text()
            if err:
                message = json.loads(err).get("message")
                code = json.loads(err).get("code")
                if code:
                    DownstreamServiceError(message=message, code=code, status_code=response_status)


class ApiTamTam(BaseApiTamTam):
    async def send_json(self, chat_id, jsn):
        url_init = urljoin(config.TAM_TAM_URL_MESSAGE, f"?chat_id={chat_id}&access_token={config.TAM_TAM_TOKEN}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url_init, json=jsn) as response:
                await self.check_errors(response)

    async def get_pool_messages(self, marker: int = 0):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self._get_tamram_url(marker=marker), timeout=config.REQUEST_TIMEOUT) as response:
                await self.check_errors(response)

    def _get_tamram_url(self, marker: int = 0) -> str:
        if marker == 0:
            return urljoin(config.TAM_TAM_URL, f"updates?access_token={config.TAM_TAM_TOKEN}")
        return urljoin(config.TAM_TAM_URL, f"updates?access_token={config.TAM_TAM_TOKEN}&marker={marker}")



# async def main():
#     api = ApiTamTam()
#     await api.send_json(-66907885424, {"text": "hello"})
#
#
# asyncio.run(main())