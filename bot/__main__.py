import logging
import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


bot = commands.Bot(command_prefix="!")


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


bot.run(os.environ["DISCORD_BOT_TOKEN"])
