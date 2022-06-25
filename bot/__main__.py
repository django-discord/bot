import inspect
import logging
import os

import commands
import crescent
import events
from dotenv import load_dotenv

_LOG_PREFIX = "[BOT]"
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if os.name != "nt":
    import uvloop

    uvloop.install()


bot = crescent.Bot(token=os.environ["DISCORD_BOT_TOKEN"])

for module in inspect.getmembers(commands, predicate=inspect.ismodule):
    bot.plugins.load(f"commands.{module[0]}")
    logger.info(f"{_LOG_PREFIX} Loading module commands.{module[0]}.")

for module in inspect.getmembers(events, predicate=inspect.ismodule):
    bot.plugins.load(f"events.{module[0]}")
    logger.info(f"{_LOG_PREFIX} Loading module events.{module[0]}.")

bot.run()
