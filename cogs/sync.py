"""Cog for syncing commands with Discord"""
from discord.ext import commands



class Owner(commands.Cog):
    """Cog for syncing commands with Discord"""
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx):
        """Sync commands with Discord"""
        await ctx.bot.tree.sync()
        await ctx.send("Commands synced, you will need to reload Discord to see them")
        await ctx.message.delete()

async def setup(bot):
    """Add the Owner cog to the bot"""
    await bot.add_cog(Owner(bot))
