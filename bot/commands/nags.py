import crescent
import hikari
from codeblocks import constants as codeblocks_constants
from markup import services as markup_services

plugin = crescent.Plugin("nags")


@plugin.include
@crescent.message_command(name="just ask")
async def just_ask_msg(ctx: crescent.Context, message: hikari.Message) -> None:
    await ctx.respond(
        (
            f"{message.author.mention}, "
            "don't ask to ask, just ask: See https://dontasktoask.com/"
        ),
        user_mentions=[message.author],
    )


@plugin.include
@crescent.command(name="justask", description="Nag a user to not ask to ask")
class JustAskSlash:
    user = crescent.option(hikari.User, "The user to mention", default=None)

    async def callback(self, ctx: crescent.Context) -> None:
        if self.user:
            await ctx.respond(
                (
                    f"{self.user.mention}, "
                    "don't ask to ask, just ask: See https://dontasktoask.com/"
                ),
                user_mentions=[self.user],
            )
        else:
            await ctx.respond(
                "Don't ask to ask, just ask: See https://dontasktoask.com/"
            )


@plugin.include
@crescent.command(
    name="markdown", description="How to properly format and markdown a codeblock."
)
class MarkdownCode:
    user = crescent.option(hikari.User, "The user to mention", default=None)

    async def callback(self, ctx: crescent.Context) -> None:
        message = (
            "When asking for help, you should properly markdown your code, for instance: \n\n"
            f"{codeblocks_constants.get_escaped_codeblock()}\n\n"
            f"This becomes: "
            f"{markup_services.codeblock(codeblocks_constants.get_example_code(), codeblocks_constants.Language.PYTHON)}"
        )
        if self.user:
            await ctx.respond(
                (message),
                user_mentions=[self.user],
            )
        else:
            await ctx.respond(message)
