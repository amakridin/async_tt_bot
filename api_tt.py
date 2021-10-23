import asyncio
import aiofiles
from ast import literal_eval
import logging
from urllib.parse import urljoin
import aiohttp
import config
import json
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
    def __init__(self):
        self.TAM_TAM_TOKEN = config.TAM_TAM_TOKEN
        self.TAM_TAM_URL = config.TAM_TAM_URL
        self.TAM_TAM_URL_MESSAGE = config.TAM_TAM_URL_MESSAGE
        self.REQUEST_TIMEOUT = config.REQUEST_TIMEOUT

    async def send_json(self, chat_id, jsn):
        url_init = urljoin(self.TAM_TAM_URL_MESSAGE, f"?chat_id={chat_id}&access_token={self.TAM_TAM_TOKEN}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url_init, json=jsn) as resp:
                self.check_errors(resp)

    async def get_pool_messages(self, marker: int = 0):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self._get_tamram_url(marker=marker), timeout=self.REQUEST_TIMEOUT) as resp:
                self.check_errors(resp)

    def _get_tamram_url(self, marker: int = 0) -> str:
        if marker == 0:
            return urljoin(self.TAM_TAM_URL, f"updates?access_token={self.TAM_TAM_TOKEN}")
        return urljoin(self.TAM_TAM_URL, f"updates?access_token={self.TAM_TAM_TOKEN}&marker={marker}")

    async def send_file(self, chat_id, msg, file_type: str = "image", file_path="img.png"):
        async with aiohttp.ClientSession() as session:
            json_init = {
                "text": f"{msg}",
                "attachments": [{
                    "type": file_type,
                    "payload": {
                        "token": f"{await self._upload_file(session, file_path, file_type)}"}
                }]}
            url_init = urljoin(self.TAM_TAM_URL_MESSAGE, f"?chat_id={chat_id}&access_token={self.TAM_TAM_TOKEN}")

            # we try to post file 60 times (it's about 60 sec)
            # if you want to send really byg file - set try_count much more than 60
            try_count = 60
            while try_count > 0:
                async with session.post(url=url_init, json=json_init) as res:
                    if res.status == 200:
                        break
                    else:
                        await asyncio.sleep(1)
                        try_count -= 1

    async def _upload_file(self, session, file_path, file_type):
        # it's for testing sending files
        if file_type == "file":
            file_path = "Zoom.pkg"
        async with aiofiles.open(file_path, 'rb') as f:
            files = {'request_file': await f.read()}
        upload_url = await self._get_upload_token(session, file_type)

        async with session.post(url=upload_url, data=files) as r:
            t = await r.text()
            ret = literal_eval(t)
            if file_type == "image":
                url_token = [val for val in ret["photos"].values()][0]["token"]
            elif file_type == "file":
                url_token = ret['token']
            return url_token

    async def _get_upload_token(self, session, file_type):
        url = f'https://botapi.tamtam.chat/uploads?type={file_type}&access_token={self.TAM_TAM_TOKEN}'
        async with session.post(url=url) as r:
            jsn = await r.json()
            return jsn['url']
