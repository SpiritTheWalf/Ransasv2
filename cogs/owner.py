"""This module contains Owner commands"""
import asyncio
import os
import sys
from typing import Optional
import discord
import sqlalchemy
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import ExtensionFailed, GuildNotFound
from sqlalchemy.exc import SQLAlchemyError
from utils.checks import is_owner, owner_or_dev
from utils.logger import logger
from database.makedb import Logs, Session


class Owner(commands.Cog):
    """Owner commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: sqlalchemy.Session = Session()

    @commands.command(name="sync", hidden=True)
    @commands.check(is_owner)
    async def sync(self, ctx: commands.context) -> None:
        """Command to sync the tree"""
        await ctx.bot.tree.sync()
        await ctx.send("Commands synced, you will need to reload Discord to see them")
        await ctx.message.delete()

    @commands.command(name="list_cogs", hidden=True)
    @commands.check(is_owner)
    async def list_cogs(self, ctx: commands.context) -> None:
        """List all loaded cogs"""
        loaded_cogs = "\n".join(self.bot.cogs.keys())
        await ctx.send(f"Loaded Cogs:\n{loaded_cogs}")
        await ctx.message.delete()

    @commands.command(name="say", hidden=True)
    @commands.check(is_owner)
    async def say(self, ctx: commands.context, *, message: Optional[str] = None) -> None:
        """Make the bot say something"""
        attachments = ctx.message.attachments
        if message is None and not attachments:
            await ctx.send("You need to provide either a message or an attachment")
            return
        try:
            if attachments:
                for attachment in attachments:
                    file = await attachment.to_file()
                    if message:
                        await ctx.send(message, file=file)
                    else:
                        await ctx.send(file=file)
            else:
                await ctx.send(message)
        finally:
            await ctx.message.delete()

    @commands.command(name="amicute", hidden=True)
    @commands.check(owner_or_dev)
    async def amicute(self, ctx: commands.context, user: Optional[discord.Member] = None) -> None:
        """Everyone is cute apart from SpiritTheWalf!!"""
        if user is None:
            user = ctx.author
        if user.id == 1174000666012823565:
            spirit = self.bot.get_user(1174000666012823565)
            await ctx.send(f"{spirit.mention} is **NOT** a cutie!")
        elif user.id == 1202981342145544212:
            luna = self.bot.get_user(1202981342145544212)
            await ctx.send(f"{luna.mention} is an **EXTRA** cutie!")
        elif user.id == 485213817958039573:
            niic = self.bot.get_user(485213817958039573)
            await ctx.send(f"{niic.mention} is...\n# THE CUTEST!!!")
        else:
            await ctx.send(f"{user.mention} is a cutie!")

    @commands.command(name="dotstatus", hidden=True)
    @commands.check(is_owner)
    async def dotstatus(self, ctx: commands.context, *, status: discord.Status) -> None:
        """Change the bot's presence status"""
        status = status.lower()
        presence_status = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.do_not_disturb,
            "offline": discord.Status.offline
        }.get(status)
        if presence_status is None:
            await ctx.send("Invalid status, please use one of the following: "
                           "online, idle, dnd, offline")
            return
        await self.bot.change_presence(status=presence_status)
        await ctx.send(f"Bot status changed to {status.capitalize()}")
        await ctx.message.delete()
        logger.info(msg=f"Spirit changed bot status to {status.capitalize()}")

    @commands.command(name="nickname", hidden=True)
    @commands.check(is_owner)
    async def nickname(self, ctx: commands.context, *, new_nickname: str) -> None:
        """Change the bot's nickname"""
        for guild in self.bot.guilds:
            try:
                await guild.me.edit(nick=new_nickname)
                await ctx.send(f"Bot nickname changed to {new_nickname}.")
            except GuildNotFound as e:
                await ctx.send(f"Failed to change bot nickname in {guild.name}: {e}.")

            await ctx.message.delete()
            logger.info("Spirit changed bot nickname to %s.", new_nickname)

    @commands.command(name="status", hidden=True)
    @commands.check(is_owner)
    async def status(self, ctx: commands.context, new_status: Optional[str] = None) -> None:
        """Change the bot's status"""
        if new_status is None:
            await self.bot.change_presence(activity=discord.Game(name=
                                        f"Patch {self.bot.version}"))
        else:
            await self.bot.change_presence(activity=discord.Game(name=new_status))
        await ctx.message.delete()
        logger.info("%s changed bot status", ctx.author)

    @commands.command(name="glist", hidden=True)
    @commands.check(is_owner)
    async def glist(self, ctx: commands.context) -> None:
        """List all guilds the bot is in"""
        guilds = self.bot.guilds
        guild: discord.Guild = ctx.guild
        content = ""
        for guild in guilds:
            line = f"{guild.name} - ID: {guild.id}\n"
            if len(content) + len(line) > 4000:
                await ctx.send(content)
                content = ""
            content += line
        if content:
            await ctx.send(content)
        await ctx.message.delete()
        logger.info(msg=f"Spirit ran command glist in {guild}")

    @commands.command(name="ginfo", hidden=True)
    @commands.check(is_owner)
    async def ginfo(self, ctx: commands.context, guild_id: Optional[int] = None) -> None:
        """Get information about a guild"""
        if guild_id is None:
            guild_id: discord.Guild.id  = ctx.guild.id

        guild = self.bot.get_guild(guild_id)
        if guild is not None:
            owner: discord.Guild.owner = guild.owner
            total_members = guild.member_count
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            created_at = guild.created_at.strftime('%Y-%m-%d %H:%M:%S')
            bot_member = guild.get_member(self.bot.user.id)
            joined_at = bot_member.joined_at.strftime('%Y-%m-%d %H:%M:%S')

            embed = discord.Embed(title=f"Guild information - {guild.name}",
                                  color=discord.Color.blue())
            embed.add_field(name="Owner", value=f"{owner.name}", inline=False)
            embed.add_field(name="Total Members", value=total_members, inline=False)
            embed.add_field(name="Text Channels", value=text_channels, inline=False)
            embed.add_field(name="Voice Channels", value=voice_channels, inline=False)
            embed.add_field(name="Created At", value=created_at, inline=False)
            embed.add_field(name="Bot Joined At", value=joined_at, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Guild not found")

        await ctx.message.delete()
        logger.info("Spirit ran command ginfo in %s ", guild.name)

    @commands.command(name="senddm", hidden=True)
    @commands.has_permissions(kick_members=True, administrator=True)
    async def senddm(self, ctx: commands.context, user_id: discord.User.id, *, message: str) -> None:
        """Send a DM to a user"""
        user = self.bot.get_user(user_id)
        guild = ctx.guild
        author = ctx.author
        if user is not None:
            try:
                await user.send(f" \\- {message}\n\nSent by {author} from guild {guild}")
                await ctx.send("Done")
            except discord.HTTPException:
                await ctx.send(f"Failed to send a message to {user.name}.")
        else:
            await ctx.send("User not found.")

        logger.info(msg=f"{author} sent a message to {user} for"
                        f" reason {message} in guild {guild}")

    @commands.command(name='restart', hidden=True)
    @commands.check(is_owner)
    async def restart(self, ctx: commands.context) -> None:
        """Restart the bot"""
        await ctx.send('Restarting...')
        await self.bot.http.close()
        await self.bot.close()
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(name="killswitch", hidden=True)
    @commands.check(is_owner)
    async def killswitch(self, ctx: commands.context, password: Optional[str] = None) -> None:
        """Stop the bot"""
        correct_password = "ThisIsAVerySecurePassword"

        if password is None:
            await ctx.send("Password required")
            await ctx.message.delete()
        elif password == correct_password:
            await ctx.send("Killswitch... ENGAGE!")
            await self.bot.close()
        else:
            await ctx.send("Wrong Password!")
            await ctx.message.delete()

    @commands.command(name="reload", hidden=True)
    @commands.check(is_owner)
    async def reload(self, ctx: commands.context, cog: commands.Cog) -> None:
        """Reload a cog"""
        message = await ctx.send(f"Reloading {cog}")
        try:
            if cog in self.bot.extensions:
                await self.bot.reload_extension(cog)
                await asyncio.sleep(5)  # Adjust sleep time as needed
                await message.edit(content=f"Reloaded {cog} successfully!")
            else:
                await ctx.send(f"Cog {cog} not found")
        except ExtensionFailed as e:
            print(f"An error occurred while reloading extension: {e}")
            await message.edit(content=f"Failed to reload {cog}")
        await ctx.message.delete()

    @app_commands.command(name="addlog", description="Manually add a guild to the DB")
    @commands.has_permissions(manage_guild=True)
    async def addlog(self, inter: discord.Interaction, guild_id: discord.Guild.id) -> None:
        """Command to manually add a log entry to the database with
                                only the guild ID."""

        guild = self.bot.get_guild(int(guild_id))
        if guild is None:
            await inter.response.send_message(f"The guild with ID {guild_id} does not exist"
                                              "or is not accessible.", ephemeral=True)
            return

        existing_entry = self.session.query(Logs).filter_by(guild_id=guild_id).first()
        if existing_entry:
            await inter.response.send_message(f"A log entry for guild ID {guild_id}"
                                                "already exists.", ephemeral=True)
            return

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
            self.session.add(new_log_entry)
            self.session.commit()
            await inter.response.send_message("Successfully added log"
            f"entry for guild ID {guild_id}.", ephemeral=True)
        except SQLAlchemyError as e:
            self.session.rollback()
            await inter.response.send_message(f"Failed to add "
                                              f"log entry: {e}", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    """Setup function for Owner"""
    await bot.add_cog(Owner(bot))
