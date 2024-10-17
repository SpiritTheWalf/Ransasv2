"""Checks for the bot."""
import discord
from discord.ext import commands
from discord import app_commands

OWNER_IDS = [1174000666012823565]
DEV_IDS = [1174000666012823565, 1108126443638116382, 952344652604903435]


def is_owner(ctx):
    """Check if the user is the owner of the bot."""
    return ctx.message.author.id in OWNER_IDS


def is_dev(ctx):
    """Check if the user is a developer of the bot."""
    return ctx.message.author.id in DEV_IDS


def owner_or_dev(ctx):
    """Check if the user is the owner or a developer of the bot."""
    return ctx.message.author.id in OWNER_IDS or DEV_IDS


def owner_or_permissions(**perms):
    """Check if the user is the owner or has the required permissions."""
    async def predicate(inter: discord.Interaction):
        """Predicate for the check."""
        if inter.user.id in OWNER_IDS:
            return True
        return await commands.has_permissions(**perms).predicate(inter)

    return app_commands.check(predicate)


def cooldown_for_everyone_but_me(inter: discord.Interaction):
    """Defines a cooldown for everyone but the owner."""
    if inter.user.id in OWNER_IDS:
        return None
    return app_commands.Cooldown(1, 300.0)


def cooldown_for_everyone_but_me_sheri(inter: discord.Interaction):
    """Defines a cooldown for everyone but the owner."""
    if inter.user.id in OWNER_IDS:
        return None
    return app_commands.Cooldown(1, 20.0)
