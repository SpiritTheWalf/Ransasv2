"""Info Cog"""
import discord
import sqlalchemy.orm
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import GroupCog
from database.makedb import Logs, Session
from utils.checks import owner_or_permissions

class Info(GroupCog):
    """The info Cog itself"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: sqlalchemy.orm.Session = Session()

    async def get_logging_channels(self, guild_id: int):
        """Get the logging channels for the guild"""
        log_entry = self.session.query(Logs).filter_by(guild_id=guild_id).first()
        return log_entry

    @app_commands.command(name="messagelogs", description="Prints the message logging channel")
    @commands.check(owner_or_permissions(manage_guild=True))
    async def messagelogs(self, inter: discord.Interaction):
        """Prints the message logging channel"""
        guild_id = inter.guild.id
        log_entry = await self.get_logging_channels(guild_id)

        if log_entry and log_entry.message_logs:
            channel_id: discord.channel.id = log_entry.message_logs
            channel: discord.channel = await inter.guild.fetch_channel(channel_id)
            if channel:
                await inter.response.send_message("The message logging "
                f"channel is set to {channel.mention}", ephemeral=True)
            else:
                await inter.response.send_message("The message logging channel"
                "is not set, set it with `/setup messagelogs`", ephemeral=True)
        else:
            await inter.response.send_message("The message logging channel is "
                "not set, set it with `/setup messagelogs`", ephemeral=True)

    @app_commands.command(name="memberlogs", description="Prints the member logging channel")
    @commands.check(owner_or_permissions(manage_guild=True))
    async def memberlogs(self, inter: discord.Interaction):
        """Prints the member logging channel"""
        guild_id: discord.Guild.id = inter.guild.id
        log_entry = await self.get_logging_channels(guild_id)  # Added await

        if log_entry and log_entry.member_logs:
            channel_id = log_entry.member_logs
            channel = inter.guild.get_channel(channel_id)
            if channel:
                await inter.response.send_message("The member logging "
                f"channel is {channel.mention}.", ephemeral=True)
            else:
                await inter.response.send_message("The member logging "
                "channel is not set, set it with `/setup memberlogs`", ephemeral=True)
        else:
            await inter.response.send_message("The member logging channel "
            "is not set, set it with `/setup memberlogs`", ephemeral=True)

    @app_commands.command(name="voicelogs", description="Prints the voice logging channel")
    @commands.check(owner_or_permissions(manage_guild=True))
    async def voicelogs(self, inter: discord.Interaction):
        """Prints the voice logging channel"""
        guild_id: discord.Guild.id = inter.guild.id
        log_entry = await self.get_logging_channels(guild_id)

        if log_entry and log_entry.voice_logs:
            channel_id: discord.channel.id = log_entry.voice_logs
            channel: discord.channel = inter.guild.get_channel(channel_id)
            if channel:
                await inter.response.send_message("The voice logging "
                f"channel is {channel.mention}.", ephemeral=True)
            else:
                await inter.response.send_message("The voice logging channel is not "
                "set, set it with `/setup voicelogs`", ephemeral=True)
        else:
            await inter.response.send_message("The voice logging channel is not"
            "set, set it with `/setup voicelogs`", ephemeral=True)

    @app_commands.command(name="modlogs", description="Prints the moderation logging channel")
    @commands.check(owner_or_permissions(manage_guild=True))
    async def modlogs(self, inter: discord.Interaction):
        """Prints the moderation logging channel"""
        guild_id: discord.Guild.id = inter.guild.id
        log_entry = await self.get_logging_channels(guild_id)  # Added await

        if log_entry and log_entry.mod_logs:
            channel_id: discord.channel.id = log_entry.mod_logs
            channel: discord.channel = inter.guild.get_channel(channel_id)
            if channel:
                await inter.response.send_message("The moderation logging "
                            f"channel is {channel.mention}.", ephemeral=True)


            else:
                await inter.response.send_message("The moderation logging channel "
                        "is not set, set it with `/setup modlogs`", ephemeral=True)
        else:
            await inter.response.send_message("The moderation logging channel "
                    "is not set, set it with `/setup modlogs`", ephemeral=True)

    @app_commands.command(name="ping", description="Get my ping to Discord")
    async def ping(self, inter: discord.Interaction):
        """Get the bot's ping to Discord"""
        latency = round(self.bot.latency * 1000)
        await inter.response.send_message(f"Pong! My latency is {latency}ms.", ephemeral=True)

    @app_commands.command(name="version", description="Prints the version of the bot")
    async def version(self, inter: discord.Interaction):
        """Prints the version of the bot"""
        await inter.response.send_message("The current version of"
                                          f"Ransas is {self.bot.STAGE} {self.bot.VERSION}")

    @app_commands.command(name="links", description="Prints some useful links about me!")
    async def links(self, inter: discord.Interaction):
        """Prints some useful links"""
        github = "[GitHub](https://github.com/SpiritTheWalf/)"
        dinvite = "[Discord](https://discord.gg/sCHC7KsA7G)"
        docs = "[Docs](https://ransas.spiritthewalf.co.uk/)"
        embed = discord.Embed(
            title="Useful links!",
            color=discord.Color.from_rgb(209, 16, 22)
        )
        embed.add_field(name="", value=f"**{github}\n{dinvite}\n{docs}**")
        embed.set_footer(text=f"Ransas {self.bot.STAGE} {self.bot.VERSION}")

        await inter.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """Adds the Info cog to the bot"""
    await bot.add_cog(Info(bot))
