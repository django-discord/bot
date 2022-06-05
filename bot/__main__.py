import inspect
import logging
import os

import commands
import crescent
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


if os.name != "nt":
    import uvloop

    uvloop.install()


bot = crescent.Bot(token=os.environ["DISCORD_BOT_TOKEN"])

for module in inspect.getmembers(commands, predicate=inspect.ismodule):
    bot.plugins.load(f"commands.{module[0]}")

bot.run()
