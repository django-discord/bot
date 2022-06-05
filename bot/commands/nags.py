import crescent
import hikari

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
