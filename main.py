import asyncio
import logging
from urllib.parse import urljoin
import aiohttp
import api_tt
import config
from parse_json import parse_json

logging.basicConfig(filename="bot.log",
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)


class GetTamTamData:
    def __init__(self):
        self.tt_api = api_tt.ApiTamTam()

    async def run(self):
        marker = 0
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=self.get_tamram_url(marker=marker),
                                           timeout=config.REQUEST_TIMEOUT) as response:
                        messages = await response.json()
                        marker = messages['marker']
                        for message in messages['updates']:
                            asyncio.ensure_future(self.handle_message(jsn=parse_json(message)))

            except Exception as ex:
                logging.error(ex.__str__())


    async def handle_message(self, jsn):
        if jsn["text"] in ("image", "file"):
            await self.tt_api.send_file(chat_id=jsn["chat_id"], msg="i send you image", file_type=jsn["text"])
        else:
            await self.tt_api.send_json(chat_id=jsn["chat_id"],
                                        jsn={"text": jsn["text"]})

    @staticmethod
    def get_tamram_url(marker: int = 0) -> str:
        if marker == 0:
            return urljoin(config.TAM_TAM_URL, f"updates?access_token={config.TAM_TAM_TOKEN}")
        return urljoin(config.TAM_TAM_URL, f"updates?access_token={config.TAM_TAM_TOKEN}&marker={marker}")


if __name__ == "__main__":
    get_data = GetTamTamData()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_data.run())