"""Cog to setup the logging channels and muterole for the bot."""
import discord
from discord.app_commands import command
from discord.ext.commands import GroupCog, ChannelNotFound

from utils.checks import owner_or_permissions
from database.makedb import Logs, Session

class Setup(GroupCog):
    """Cog to setup the logging channels and muterole for the bot."""
    def __init__(self, bot):
        self.bot = bot
        self.session = Session()

    async def get_logging_channels(self, guild_id):
        """Use ORM to query the database"""
        return self.session.query(Logs).filter_by(guild_id=guild_id).first()

    async def update_log_channel(self, guild_id, channel_id, log_type):
        """Update the logging channel in the database"""
        log_entry = await self.get_logging_channels(guild_id)
        if log_entry:
            setattr(log_entry, log_type, channel_id)
            self.session.commit()
            return True
        return False

    async def respond_with_channel_set(self, inter, channel, log_type):
        """Respond to the user with the channel set message"""
        await inter.response.send_message(
            f"{log_type} logging channel set to {channel.mention}.",
            ephemeral=True
        )

    async def set_log_channel(self, inter: discord.Interaction,
                              channel: discord.TextChannel, log_type):
        """Set the logging channel for the guild"""
        guild_id = inter.guild_id
        if await self.update_log_channel(guild_id, channel.id, log_type):
            await self.respond_with_channel_set(inter, channel, log_type)
        else:
            await inter.response.send_message("Logs entry not "
            "found for this guild.", ephemeral=True)

    @command(name="messagelogs", description="Sets the message logging channel")
    @owner_or_permissions(manage_guild=True)
    async def messagelogs(self, inter: discord.Interaction, channel: discord.TextChannel):
        """Set the message logging channel for the guild"""
        await self.set_log_channel(inter, channel, 'message_logs')

    @command(name="memberlogs", description="Sets the member logging channel")
    @owner_or_permissions(manage_guild=True)
    async def memberlogs(self, inter: discord.Interaction, channel: discord.TextChannel):
        """Set the member logging channel for the guild"""
        await self.set_log_channel(inter, channel, 'member_logs')

    @command(name="modlogs", description="Sets the moderation logging channel")
    @owner_or_permissions(manage_guild=True)
    async def modlogs(self, inter: discord.Interaction, channel: discord.TextChannel):
        """Set the message logging channel for the guild"""
        await self.set_log_channel(inter, channel, 'mod_logs')

    @command(name="voicelogs", description="Sets the voice logging channel")
    @owner_or_permissions(manage_guild=True)
    async def voicelogs(self, inter: discord.Interaction, channel: discord.TextChannel):
        """Set the voice logging channel for the guild"""
        await self.set_log_channel(inter, channel, 'voice_logs')

    async def update_database(self, guild_id, muterole_id, muterole_channel_id):
        """Update the muterole and muterole channel in the database"""
        log_entry = await self.get_logging_channels(guild_id)
        if log_entry:
            log_entry.muterole = muterole_id
            log_entry.muterole_channel = muterole_channel_id
            self.session.commit()

    @command(name="muterole", description="Sets the muterole channel and description")
    @owner_or_permissions(manage_guild=True)
    async def muterole(self, inter: discord.Interaction, role: discord.Role,
                       channel: discord.TextChannel):
        """Set the muterole and muterole channel for the guild"""
        guild_id = inter.guild_id
        await inter.response.defer()
        try:
            await self.update_database(guild_id, role.id, channel.id)

            channels = inter.guild.text_channels + inter.guild.voice_channels

            for c in channels:
                current_overwrites = c.overwrites_for(role)
                if c != channel:
                    current_overwrites.update(
                        send_messages=False,
                        read_messages=False,
                        connect=False
                    )
                else:
                    current_overwrites.update(
                        send_messages=True,
                        read_messages=True,
                        connect=False
                    )
                await c.set_permissions(role, overwrite=current_overwrites)

            await inter.followup.send(f"{role.mention} has been muted in "
            f"all channels except {channel.mention}.", ephemeral=True)
        except ChannelNotFound as e:
            print(f"An error occurred: {e}")

async def setup(bot):
    """Add the cog to the bot"""
    await bot.add_cog(Setup(bot))
