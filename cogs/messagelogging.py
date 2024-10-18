"""Message logging cog for the bot."""
from datetime import datetime, timezone, timedelta
import discord
import sqlalchemy.orm
from discord.ext import commands
from discord.ext.commands import ChannelNotFound

from database.makedb import Logs, Session


class LoggingCog(commands.Cog):
    """Logging cog for the bot."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: sqlalchemy.orm.Session = Session()

    async def get_logging_channels(self, guild_id: int):
        """Get the logging channels for the given guild ID."""
        return self.session.query(Logs).filter_by(guild_id=guild_id).first()

    async def send_join_leave_logging_embed(self, guild, action, member, reason=None):
        """Send a join/leave logging embed to the logging channel."""
        guild_id = guild.id
        log_entry = await self.get_logging_channels(guild_id)

        if log_entry:
            channel_id = log_entry.member_logs
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title=f"Member {action}",
                    color=discord.Color.green() if action == "joined" else discord.Color.red()
                )
                embed.set_author(name=member.display_name,
                icon_url=member.avatar.url if member.avatar else None)

                embed.add_field(name="User", value=member.mention, inline=False)
                embed.add_field(name="User ID", value=member.id, inline=False)
                embed.add_field(name="Account creation date",
                value=member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
                embed.add_field(name="Timestamp",
                value=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)

                if reason:
                    embed.add_field(name="Reason", value=reason.capitalize(), inline=False)

                try:
                    await channel.send(embed=embed)
                except ChannelNotFound as e:
                    print(f"Error sending message: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send a join logging embed when a member joins the server."""
        guild = member.guild
        await self.send_join_leave_logging_embed(guild, "joined", member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Send a leave logging embed when a member leaves the server."""
        guild = member.guild
        reason = None

        cutoff_time = datetime.now().replace(tzinfo=timezone.utc) - timedelta(seconds=30)

        async for entry in guild.audit_logs(action=discord.AuditLogAction.kick):
            if entry.target == member and entry.created_at > cutoff_time:
                reason = "Kicked"
                break

        await self.send_join_leave_logging_embed(guild, "left", member, reason)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Send a message edit logging embed when a message is edited."""
        if before.author.bot:
            return

        if before.content == after.content:
            return

        guild_id = before.guild.id
        log_entry = await self.get_logging_channels(guild_id)

        if log_entry:
            channel_id = log_entry.message_logs
            channel = before.guild.get_channel(channel_id)

            if channel:
                embed = discord.Embed(
                    title="Message Edited",
                    color=discord.Color.gold()
                )

                embed.add_field(name="Before", value=before.content or
                                                     "[No Text Content]", inline=False)
                embed.add_field(name="After", value=after.content or
                                                    "[No Text Content]", inline=False)
                embed.add_field(name="Author", value=before.author.mention, inline=False)
                embed.add_field(name="Channel", value=before.channel.mention, inline=False)
                embed.add_field(name="Timestamp", value=datetime.now(tz=timezone.utc).strftime
                                                    ("%Y-%m-%d %H:%M:%S UTC"), inline=False)

                try:
                    await channel.send(embed=embed)
                except ChannelNotFound as e:
                    print(f"Failed to send message in channel {channel_id}: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Send a voice channel logging embed when a member joins or leaves a voice channel."""
        guild_id = member.guild.id
        log_entry = await self.get_logging_channels(guild_id)

        if log_entry:
            channel_id = log_entry.voice_logs
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(color=discord.Color.blurple())
                embed.set_author(name=member.display_name, icon_url=member.avatar.url)

                if before.channel is None and after.channel is not None:
                    embed.title = "Voice channel joined"
                    embed.add_field(name="Channel", value=after.channel.mention, inline=False)
                    embed.add_field(name="Timestamp",
                    value=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                                    inline=False)
                    await channel.send(embed=embed)

                elif before.channel is not None and after.channel is None:
                    embed.title = "Voice channel left"
                    embed.add_field(name="Channel", value=before.channel.mention, inline=False)
                    embed.add_field(name="Timestamp",
                    value=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                                    inline=False)
                    await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Send a message delete logging embed when a message is deleted."""
        if message.author.bot:
            return
        guild_id = message.guild.id
        log_entry = await self.get_logging_channels(guild_id)

        if log_entry:
            channel_id = log_entry.message_logs
            channel = message.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="Message Deleted",
                    color=discord.Color.red()
                )
                embed.add_field(name="Content", value=message.content, inline=False)
                embed.add_field(name="Author", value=message.author.mention, inline=False)
                embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                embed.add_field(name="Timestamp",
                value=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
                await channel.send(embed=embed)


async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(LoggingCog(bot))
