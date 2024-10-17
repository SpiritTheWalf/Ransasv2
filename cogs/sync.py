"""Cog for syncing commands with Discord"""
import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.exc import SQLAlchemyError
from database.models import Logs, Session

class Owner(commands.Cog):
    """Cog for syncing commands with Discord"""
    def __init__(self, bot):
        self.bot = bot
        self.session = Session()


    @commands.command(name="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx):
        """Sync commands with Discord"""
        await ctx.bot.tree.sync()
        await ctx.send("Commands synced, you will need to reload Discord to see them")
        await ctx.message.delete()

    @app_commands.command(name="addlog", description="Manually add a guild to the DB")
    @commands.has_permissions(manage_guild=True)  # Ensure only admins can use this command
    async def addlog(self, inter: discord.Interaction, guild_id: str):
        """Command to manually add a log entry to the database with only the guild ID."""

        # Check if the guild exists
        guild = self.bot.get_guild(int(guild_id))
        if guild is None:
            await inter.response.send_message(f"The guild with ID {guild_id} does not exist"
                                              "or is not accessible.", ephemeral=True)
            return

        # Check if a log entry already exists for this guild
        existing_entry = self.session.query(Logs).filter_by(guild_id=guild_id).first()
        if existing_entry:
            await inter.response.send_message(f"A log entry for guild ID {guild_id}"
                                                "already exists.", ephemeral=True)
            return

        # Create a new Logs object with the provided guild_id and other fields set to None
        new_log_entry = Logs(
            guild_id=guild_id,
            message_logs=None,
            member_logs=None,
            voice_logs=None,
            mod_logs=None,
            muterole=None,
            muterole_channel=None
        )

        try:
            # Add the new entry to the session and commit
            self.session.add(new_log_entry)
            self.session.commit()
            await inter.response.send_message("Successfully added log"
            f"entry for guild ID {guild_id}.", ephemeral=True)
        except SQLAlchemyError as e:
            self.session.rollback()  # Rollback in case of error
            await inter.response.send_message(f"Failed to add log entry: {e}", ephemeral=True)

async def setup(bot):
    """Add the Owner cog to the bot"""
    await bot.add_cog(Owner(bot))
