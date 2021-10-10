import logging

logging.basicConfig(filename="bot.log", level=logging.ERROR)


class BaseError(Exception):
    message: str = "Unexpected exception"
    code: str = "unexpected_exception"
    status_code: int = 500
    logging.error(f"status_code: {status_code}, code: {code}, message: {message}")


class DownstreamServiceError(BaseError):
    def __init__(self, message: str, code: str, status_code: int = 400) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        logging.error(f"status_code: {status_code}, code: {code}, message: {message}")

        super().__init__()


