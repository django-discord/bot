import logging
import os

import hikari
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


bot = hikari.GatewayBot(token=os.environ["DISCORD_BOT_TOKEN"])


@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    if event.content.startswith("!ping"):
        await event.message.respond("pong!")


bot.run()
