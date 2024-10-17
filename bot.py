"""
This is the main file for the bot.
It contains the bot class and the main function to run the bot.
"""

import os
import traceback
import discord

from discord.ext import commands
from discord.ext.commands import ExtensionError
from dotenv import load_dotenv


load_dotenv()
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.members = True


async def cog_loader(bot_instance):
    """This function loads all cogs in the cogs folder plus jishaku."""
    await bot_instance.load_extension('jishaku')
    for file in os.listdir('./cogs'):
        if file.endswith('.py') and file != '__init__.py':
            cog_name = file[:-3]
            try:
                await bot_instance.load_extension(f'cogs.{cog_name}')
                print(f'Successfully loaded {cog_name}')
            except  ExtensionError as e:
                print(f'Failed to load cog {cog_name}: {str(e)}')
                print(traceback.format_exc())

class RansasV2(commands.Bot):
    """This is the main bot class."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        """This function is called after the bot is ready."""
        await cog_loader(self)

    async def on_ready(self):
        """This function is called when the bot is ready."""
        print(f'Logged in as {self.user.name}')
        print("Ready to recieve commands!")

bot = RansasV2(command_prefix='r!', intents=intents)

if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
