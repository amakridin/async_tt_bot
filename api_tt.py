import asyncio
import json
import logging
from urllib.parse import urljoin

import aiohttp

import config
from errors import DownstreamServiceError

logging.basicConfig(filename="bot.log",
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)


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

    async def send_photo(self, chat_id, msg, img_path="img.png"):
        url = f'https://botapi.tamtam.chat/uploads?type=image&access_token={config.TAM_TAM_TOKEN}'
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url) as r:
                jsn = await r.json()
                url_load = jsn['url']
                files = {'request_file': open(img_path, 'rb')}
            async with session.post(url=url_load, data=files) as r:
                t = await r.text()
                ret = eval(t)
                for key in (ret['photos'].keys()):
                    url_token = ret['photos'][key]['token']
                    json_init = {
                        "text": f"{msg}",
                        "attachments": [{
                            "type": "image",
                            "payload": {
                                "token": f"{url_token}"}
                        }]}
            url_init = urljoin(config.TAM_TAM_URL_MESSAGE, f"?chat_id={chat_id}&access_token={config.TAM_TAM_TOKEN}")
            async with session.post(url=url_init, json=json_init) as res:
                await self.check_errors(res)
