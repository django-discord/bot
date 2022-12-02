import crescent
import hikari
from codeblocks.parsers import get_parser, should_parse_message

plugin = crescent.Plugin("codeblocks")


@plugin.include
@crescent.event
async def on_message_format(event: hikari.MessageCreateEvent):
    if event.message.author.is_bot or event.message.content is None:
        return
    if not should_parse_message(event.message.content):
        return

    codeblock = get_parser(message=event.message)
    if codeblock is not None:
        await event.message.respond(
            "Please use the slash command `/markdown` for more information on how to properly format your code.",
            reply=True,
            mentions_reply=True,
        )
        await event.message.respond(
            codeblock.validate_and_format().content,
            reply=True,
            mentions_reply=True,
        )
