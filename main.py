import asyncio
import json
import pathlib
import textwrap
import logging
import typing

import decouple
import discord
from discord.ext import commands
from discord.ext.tasks import loop
from discord.ext.commands import Context

import rss.converter
from rss.feed import RSSFeed

config = decouple.config

MESSAGE_LIMIT = config("DISCORD_MAX_MESSAGE_LENGTH", cast=int)
DISCORD_ERROR_USER_IDS = config("DISCORD_ERROR_USER_IDS", cast=list[str])

with open("feeds.json", "r") as file:
    feed_specifications = json.load(file)


feeds = {}
for name, feed_spec in feed_specifications.items():
    feed = RSSFeed(
        url=feed_spec.get("url"),
        name=name,
        converter=rss.converter.load_converter(feed_spec.get("converter"))(),
    )

    feeds.update({feed_spec.get("destination_channel_id"): feed})


discord.utils.setup_logging()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents)

LOCAL_AUDIO_FILE_PATH = "audio"


def is_post_already_in_channel(post, channel) -> bool:
    return any((thread.name == post.title) for thread in channel.threads)


async def sync_feed(into_channel_id: int, feed: RSSFeed):
    channel = await bot.fetch_channel(into_channel_id)

    posts = feed.posts()

    # If we don't have any threads, then start creating the last posts first
    # This is just to at least try to preserve the order of posts
    # Note, this may not *actually* work, we assume that the rss feed is sorted
    # in chronological order to begin with
    if not channel.threads:
        posts = reversed([post for post in posts])

    for post in posts:
        logging.info(f"Found post '{post.title}'")

        if is_post_already_in_channel(post, channel):
            logging.info("Post already present. We are up to date!")
            break

        logging.info("Creating new post")
        content = post.render_content()
        thread_with_message = await channel.create_thread(
            name=post.title, content=content[:MESSAGE_LIMIT], suppress_embeds=True
        )

        if len(content) < MESSAGE_LIMIT:
            continue

        for chunk in textwrap.wrap(content[:MESSAGE_LIMIT], MESSAGE_LIMIT):
            await thread_with_message.thread.send(chunk, suppress_embeds=True)


@loop(seconds=config("RSS_SYNC_INTERVAL_SECONDS", cast=int))
@commands.has_permissions(kick_members=True)
@discord.app_commands.guild_only()
async def sync_feeds():
    """Fetches posts from feeds and inserts them (if not already present) into the channel id (dict key)."""
    for channel_id, feed in feeds.items():
        logging.info(f"Fetching feed '{feed.name}'")

        await sync_feed(into_channel_id=channel_id, feed=feed)


@bot.hybrid_command(name="justask", description="Nag a user to not ask to ask")
@discord.app_commands.describe(user="The user to mention")
@discord.app_commands.guild_only()
async def just_ask(ctx, user: typing.Optional[discord.User]):
    if user:
        await ctx.reply(
            f"<@{user.id}>, don't ask to ask, just ask: https://dontasktoask.com"
        )
        return

    await ctx.reply("Don't ask to ask, just ask: https://dontasktoask.com")


async def sound_files_autocomplete(_: discord.Interaction, current: str) -> typing.List[discord.app_commands.Choice[str]]:
    files = [
        discord.app_commands.Choice(name=f"{file.stem} ({file.suffix})", value=str(file))
        for file in pathlib.Path(LOCAL_AUDIO_FILE_PATH).iterdir()
        if file.is_file() and current in file.name
    ]

    return files


@bot.hybrid_command(name="sequentialplayback", description="Joins a channel, plays the sound and continues to the next channel.")
@discord.app_commands.describe(sound="The sound to play")
@discord.app_commands.describe(volume="Float volume multiplier to apply to the audio (example: 0.5 for halving the playback volume)")
@discord.app_commands.describe(channels="Channel ids (space separated) which should be joined")
@discord.app_commands.autocomplete(sound=sound_files_autocomplete)
@commands.has_permissions(kick_members=True)
@discord.app_commands.guild_only()
async def sequential_playback(ctx: Context, sound, volume: float, channels: commands.Greedy[int]):
    await ctx.reply("Starting up")

    voice_channel = discord.utils.get(ctx.bot.voice_clients)
    if voice_channel.is_connected():
        await ctx.reply(
            "I'm already connected to a voice channel. Either wait for me to do my thing, "
            "or forcefully disconnect me if you think there has been a problem."
        )
        return

    for channel_id in channels:
        channel = bot.get_channel(channel_id)
        if not isinstance(channel, discord.VoiceChannel):
            await ctx.reply(f"{channel_id} is not a valid voice channel id. I'm going to skip it.")
            continue

        voice_channel: discord.VoiceClient = await channel.connect()
        voice = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(sound), volume=volume)
        voice_channel.play(voice)
        while voice_channel.is_playing():
            await asyncio.sleep(.1)

        await voice_channel.voice_disconnect()
        await voice_channel.disconnect()

    await ctx.reply("Finished")


@bot.hybrid_command(name="sync", description="Synchronize all the bot's commands")
@commands.has_permissions(kick_members=True)
@discord.app_commands.guild_only()
async def sync(ctx: Context):
    await bot.tree.sync()
    await ctx.reply("Finished sync")


@bot.event
async def on_ready():
    logging.info(f"Logged on as {bot.user}!")
    sync_feeds.start()


@bot.event
async def on_error(event_method: str, /, *_) -> None:
    # This, of course, won't work if discord itself is having issues
    logging.error(f"An error occurred in the event method: {event_method}")

    for user_id in DISCORD_ERROR_USER_IDS:
        DISCORD_ERROR_USER_IDS.remove(user_id)
        logging.info(f"Sending error message to user: {user_id}")

        user = await bot.fetch_user(user_id)

        await user.send(
            f"Howdy there!\n"
            f"A runtime error occurred in the function '{event_method}'.\n"
            "You may say, that's a useless logging message.\n"
            "**You are right.**\n"
            "But sending exception traces with potentially sensitive information on discord seems like a bad idea "
            "¯\\_(ツ)_/¯.\n"
            "I'll go with the ostrich algorithm on this one (https://en.wikipedia.org/wiki/Ostrich_algorithm)."
        )
        await user.send(
            f"In order to let you enhance your calm (HTTP 420 - hehehe), "
            f"i will not be sending ANY other error messages until i get restarted, "
            f"and this issue is - hopefully - resolved."
        )


if __name__ == "__main__":
    bot.run(config("DISCORD_TOKEN"))
