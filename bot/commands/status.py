import crescent

plugin = crescent.Plugin("status")


@plugin.include
@crescent.command
async def ping(ctx: crescent.Context):
    await ctx.respond("pong!")
