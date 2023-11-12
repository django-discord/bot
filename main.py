#!/usr/bin/env python
"""Entry point."""
import asyncio
import json
import logging
import os
import pathlib
import textwrap

import discord
import dotenv
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.tasks import loop

import rss.converter
from rss.feed import RSSFeed
from rss.post import Post

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = pathlib.Path(__file__).parent
AUDIO_DIRECTORY = BASE_DIR / "audio"

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DISCORD_ERROR_USER_IDS = map(
    int, os.environ.get("DISCORD_ERROR_USER_IDS", default="").split(",")
)
MESSAGE_LIMIT = int(os.environ.get("DISCORD_MAX_MESSAGE_LENGTH", default="2000"))
RSS_SYNC_INTERVAL_SECONDS = int(
    os.environ.get("RSS_SYNC_INTERVAL_SECONDS", default="120")
)


class NotForumChannelError(Exception):
    """Raised when a channel is not a forum type channel."""


with (BASE_DIR / "feeds.json").open() as file:
    feed_specifications = json.load(file)


feeds: dict[int, RSSFeed] = {}
for name, feed_spec in feed_specifications.items():
    feed = RSSFeed(
        url=feed_spec.get("url"),
        name=name,
        converter=rss.converter.load_converter(feed_spec.get("converter"))(),
    )
    feeds |= {feed_spec.get("destination_channel_id"): feed}


discord.utils.setup_logging()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents)


def is_post_already_in_channel(post: Post, channel) -> bool:
    """Check if a post is already in a channel."""
    return any((thread.name == post.title) for thread in channel.threads)


async def sync_feed(channel_id: int, feed: RSSFeed) -> None:
    """Synchronise an RSS feed with a channel."""
    channel = await bot.fetch_channel(channel_id)
    if not isinstance(channel, discord.ForumChannel):
        raise NotForumChannelError(channel_id)
    posts = feed.posts()
    # If we don't have any threads, then start creating the last posts first
    # This is just to at least try to preserve the order of posts
    # Note, this may not *actually* work, we assume that the rss feed is sorted
    # in chronological order to begin with
    if not channel.threads:
        posts = reversed(list(posts))
    for post in posts:
        logger.info("Found post '%s'", post.title)
        if is_post_already_in_channel(post, channel):
            logger.info("Post already present. We are up to date!")
            break
        logger.info("Creating new post")
        content = post.render_content()
        thread_with_message = await channel.create_thread(
            name=post.title, content=content[:MESSAGE_LIMIT], suppress_embeds=True
        )
        if len(content) < MESSAGE_LIMIT:
            continue
        for chunk in textwrap.wrap(content[:MESSAGE_LIMIT], MESSAGE_LIMIT):
            await thread_with_message.thread.send(chunk, suppress_embeds=True)


@loop(seconds=RSS_SYNC_INTERVAL_SECONDS)
@commands.has_permissions(kick_members=True)
@discord.app_commands.guild_only()
async def sync_feeds() -> None:
    """Synchronise RSS feeds.

    Fetches posts from feeds and inserts them (if not already present)
    into the channel ID (dict key).
    """
    for channel_id, feed in feeds.items():
        logger.info("Fetching feed '%s'", feed.name)
        await sync_feed(channel_id=channel_id, feed=feed)


@bot.hybrid_command(name="justask", description="Nag a user to not ask to ask")
@discord.app_commands.describe(user="The user to mention")
@discord.app_commands.guild_only()
async def just_ask(ctx: Context, user: discord.User | None) -> None:
    """Nag a user to not ask to ask."""
    if user:
        await ctx.reply(
            f"<@{user.id}>, don't ask to ask, just ask: https://dontasktoask.com"
        )
        return
    await ctx.reply("Don't ask to ask, just ask: https://dontasktoask.com")


async def autocomplete_sound_files(
    _: discord.Interaction, current: str
) -> list[discord.app_commands.Choice[str]]:
    """Autocomplete sound files."""
    return [
        discord.app_commands.Choice(
            name=f"{file.stem} ({file.suffix})", value=str(file)
        )
        for file in AUDIO_DIRECTORY.iterdir()
        if file.is_file() and current in file.name
    ]


@bot.hybrid_command(
    name="sequentialplayback",
    description="Joins a channel, plays the sound and continues to the next channel.",
)
@discord.app_commands.describe(sound="The sound to play")
@discord.app_commands.describe(
    volume=(
        "Float volume multiplier to apply to the audio "
        "(example: 0.5 for halving the playback volume)"
    )
)
@discord.app_commands.describe(
    channels="Channel IDs (space separated) which should be joined"
)
@discord.app_commands.autocomplete(sound=autocomplete_sound_files)
@commands.has_permissions(kick_members=True)
@discord.app_commands.guild_only()
async def play_sound_in_channels(
    ctx: Context, sound: str, volume: float, channels: commands.Greedy[int]
) -> None:
    """Play a sound in multiple channels.

    This command will join a channel, play the sound, and then continue
    to the next channel until the sound has been played on all channels.
    """
    await ctx.reply("Starting up")
    voice_channel = discord.utils.get(ctx.bot.voice_clients)
    if voice_channel.is_connected():
        await ctx.reply(
            "I'm already connected to a voice channel. "
            "Either wait for me to do my thing, "
            "or forcefully disconnect me if you think there has been a problem."
        )
        return
    for channel_id in channels:
        channel = bot.get_channel(channel_id)
        if not isinstance(channel, discord.VoiceChannel):
            await ctx.reply(
                f"{channel_id} is not a valid voice channel id. I'm going to skip it."
            )
            continue
        voice_channel: discord.VoiceClient = await channel.connect()
        voice = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(sound), volume=volume
        )
        voice_channel.play(voice)
        while voice_channel.is_playing():
            await asyncio.sleep(0.1)
        await voice_channel.voice_disconnect()
        await voice_channel.disconnect()
    await ctx.reply("Finished")


@bot.hybrid_command(name="sync", description="Synchronize all the bot's commands")
@commands.has_permissions(kick_members=True)
@discord.app_commands.guild_only()
async def sync(ctx: Context) -> None:
    """Synchronize all the bot's commands."""
    await bot.tree.sync()
    await ctx.reply("Finished sync")


@bot.event
async def on_ready() -> None:
    """Event handler for when the bot is ready."""
    logger.info("Logged on as %s!", bot.user)
    sync_feeds.start()


@bot.event
async def on_error(event_method: str, /, *_) -> None:
    """Event handler for when an error occurs."""
    # This, of course, won't work if discord itself is having issues
    logger.error("An error occurred in the event method: %s", event_method)
    for user_id in DISCORD_ERROR_USER_IDS:
        logger.info("Sending error message to user: %s", user_id)
        user = await bot.fetch_user(user_id)
        await user.send(
            "Howdy there!\n"
            f"A runtime error occurred in the function '{event_method}'.\n"
        )
        await user.send(
            "In order to let you enhance your calm (HTTP 420 - hehehe), "
            "i will not be sending ANY other error messages until i get restarted, "
            "and this issue is - hopefully - resolved."
        )


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
