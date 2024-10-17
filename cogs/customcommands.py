"""Custom Commands Cog"""
from datetime import datetime, timezone
import traceback
import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.exc import NoResultFound, NotSupportedError
from database.makedb import Session, CC as CustomCommand

class NotOwner(app_commands.CheckFailure):
    """Exception raised when the user is not the owner of the bot."""

async def is_owner(interaction: discord.Interaction):
    """Check if the user is the owner of the bot."""
    if not await interaction.client.is_owner(interaction.user):
        await interaction.response.send_message("You do not have permission"
        " to use this command!", ephemeral=True)
        raise NotOwner("You are not my owner!")
    return True


class CustomCommands(commands.Cog):
    """Custom Commands Cog"""
    def __init__(self, bot):
        self.bot = bot
        self.session = Session()

    async def name_autocomplete(self, inter: discord.Interaction, current: str):
        """Provide autocomplete options for custom commands."""
        try:
            is_nsfw = inter.channel.is_nsfw()

            ccommands = self.session.query(CustomCommand).filter(
                CustomCommand.name.like(f"%{current}%")).all()

            filtered_results = [cmd for cmd in ccommands if is_nsfw or not cmd.nsfw]

            return [app_commands.Choice(name=cmd.name, value=cmd.name) for cmd in filtered_results]
        finally:
            self.session.close()

    @app_commands.command(name="cc_add", description="Add a custom command to the database")
    @app_commands.check(is_owner)
    async def add(self, inter: discord.Interaction, name: str, owner: discord.Member,
                  nsfw: bool, text: str, image: str = None):
        """Add a custom command to the database."""
        try:
            owner_id = owner.id
            created_at = datetime.now(timezone.utc)

            existing_command = self.session.query(CustomCommand).filter_by(name=name).first()
            if existing_command:
                await inter.response.send_message("A custom command with the "
                f"name '{name}' already exists.", ephemeral=True)
                return

            new_command = CustomCommand(
                name=name,
                owner_id=owner_id,
                created_at=created_at,
                text=text,
                image=image,
                nsfw=nsfw
            )
            self.session.add(new_command)
            self.session.commit()

            await inter.response.send_message("Custom "
            f"command '{name}' added for {owner.mention}", ephemeral=True)
        except NotSupportedError as e:
            traceback.print_exc()
            await inter.response.send_message(f"An error occurred!\n\n{e}", ephemeral=True)
            self.session.rollback()
        finally:
            self.session.close()

    @app_commands.command(name="cc", description="View custom command")
    async def cc(self, inter: discord.Interaction, name: str):
        """View a custom command."""
        try:
            command = self.session.query(CustomCommand).filter_by(name=name).first()
            if command:
                image = command.image
                text = command.text

                if inter.channel.is_nsfw() or not command.nsfw:
                    if image:
                        embed = discord.Embed(title=text)
                        embed.set_image(url=image)
                        await inter.response.send_message(embed=embed)
                    else:
                        await inter.response.send_message(text)
                else:
                    await inter.response.send_message(
                        "This custom command is NSFW and can only be used in "
                        "NSFW channels.\n\n-# If you believe this "
                        "is a mistake, please contact SpiritTheWalf."
                    )
            else:
                await inter.response.send_message("No custom command found with that name.")
        except NotSupportedError as e:
            traceback.print_exc()
            await inter.response.send_message(f"An error occurred!\n\n{e}")
        finally:
            self.session.close()

    @cc.autocomplete('name')
    async def autocomplete_name(self, inter: discord.Interaction, current: str):
        """Provide autocomplete options for custom commands."""
        await self.name_autocomplete(inter, current)

    @app_commands.command(name="cc_delete", description="Delete a Custom Command")
    @app_commands.check(is_owner)
    async def cc_delete(self, inter: discord.Interaction, name: str):
        """Delete a custom command."""
        try:
            command = self.session.query(CustomCommand).filter_by(name=name).first()
            if command:
                self.session.delete(command)
                self.session.commit()
                await inter.response.send_message(f"Custom command '{name}' "
                                                    "deleted successfully", ephemeral=True)

            else:
                await inter.response.send_message(f"No custom command"
                f" named '{name}' found.", ephemeral=True)
        except NotSupportedError as e:
            traceback.print_exc()
            await inter.response.send_message("An error occurred while "
                                              f"deleting the command '{name}'. Please try "
                                              f"again later.\n\n{e}", ephemeral=True)
            self.session.rollback()
        finally:
            self.session.close()


    async def get_filtered_command_names(self, current: str, is_nsfw: bool):
        """Retrieve and filter command names based on input and NSFW status."""
        try:
            if is_nsfw:
                results = self.session.query(CustomCommand).filter(
                    CustomCommand.name.like(f"%{current}%")).limit(25).all()
            else:
                results = self.session.query(CustomCommand).filter(
                    CustomCommand.name.like(f"%{current}%"),
                    CustomCommand.nsfw is False).limit(25).all()

            return [app_commands.Choice(name=command.name, value=command.name)
                    for command in results]
        except NoResultFound:
            traceback.print_exc()
            return []
        finally:
            self.session.close()


    @cc.autocomplete('name')
    async def cc_autocomplete(self, inter: discord.Interaction, current: str):
        """Provide autocomplete options for command names."""
        is_nsfw = inter.channel.is_nsfw()
        return await self.get_filtered_command_names(current, is_nsfw)

    @cc_delete.autocomplete('name')
    async def name_autocomplete_delete(self, inter: discord.Interaction, current: str):
        """Provide autocomplete options for command names in delete command."""
        is_nsfw = inter.channel.is_nsfw()
        return await self.get_filtered_command_names(current, is_nsfw)


async def setup(bot):
    """Add the CustomCommands cog to the bot."""
    await bot.add_cog(CustomCommands(bot))
