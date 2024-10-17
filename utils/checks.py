import discord
from discord.ext import commands
from discord import app_commands

OWNER_IDS = [1174000666012823565]
DEV_IDS = [1174000666012823565, 1108126443638116382, 952344652604903435]


def is_owner(ctx):
    return ctx.message.author.id in OWNER_IDS


def is_dev(ctx):
    return ctx.message.author.id in DEV_IDS


def owner_or_dev(ctx):
    return ctx.message.author.id in OWNER_IDS or DEV_IDS


def owner_or_permissions(**perms):
    async def predicate(inter: discord.Interaction):
        if inter.user.id in OWNER_IDS:
            return True
        return await commands.has_permissions(**perms).predicate(inter)

    return app_commands.check(predicate)


def cooldown_for_everyone_but_me(inter: discord.Interaction):
    if inter.user.id in OWNER_IDS:
        return None
    return app_commands.Cooldown(1, 300.0)


def cooldown_for_everyone_but_me_sheri(inter: discord.Interaction):
    if inter.user.id in OWNER_IDS:
        return None
    return app_commands.Cooldown(1, 20.0)
