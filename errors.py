import logging

logging.basicConfig(filename="bot.log",
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)


class BaseError(Exception):
    message: str = "Unexpected exception"
    code: str = "unexpected_exception"
    status_code: int = 500


class DownstreamServiceError(BaseError):
    def __init__(self, message: str, code: str, status_code: int = 400) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        logging.error(f"status_code: {status_code}, code: {code}, message: {message}")

        super().__init__()


