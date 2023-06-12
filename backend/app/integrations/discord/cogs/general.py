from discord.ext import commands


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Ping command to check bot's latency."""
        latency = self.bot.latency
        await ctx.send(f"Pong! Latency: {latency * 1000:.2f}ms")


async def setup(bot):
    await bot.add_cog(General(bot))
