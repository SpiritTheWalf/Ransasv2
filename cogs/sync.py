import discord
from discord.ext import commands
from discord import app_commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx):
        await ctx.bot.tree.sync()
        await ctx.send("Commands synced, you will need to reload Discord to see them")
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Owner(bot))