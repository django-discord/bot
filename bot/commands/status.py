import crescent

plugin = crescent.Plugin("status")


@plugin.include
@crescent.command(description="Ping the bot to check it's working")
async def ping(ctx: crescent.Context):
    await ctx.respond("pong!")
