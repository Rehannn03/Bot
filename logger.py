from loguru import logger

logger.add("bot.log",rotation="10 MB", level="INFO", format="{time} {level} {message}")