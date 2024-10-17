"""Cog for E621 commands"""
import random
import traceback

import discord

import e621 as e6

from discord import app_commands, Forbidden
from discord.ext.commands import GroupCog
from discord.app_commands import command
from discord.ui import View, Button
from dotenv import load_dotenv
from utils.blacklist import tag_blacklist

load_dotenv()


def nsfw_check(tags, ctx):
    """Checks if the channel is NSFW and adds the appropriate tag"""
    if not ctx.guild:
        return tags + " -rating:safe"
    if not ctx.channel.is_nsfw():
        tags += " rating:safe"
    else:
        return tags
    return tags


async def close_callback(inter: discord.Interaction):
    """Closes the view"""
    if inter.user.id == inter.message.interaction_metadata.user.id:
        await inter.message.edit(view=None)
        return True
    else:
        await inter.response.send_message("You can't use this button!", ephemeral=True)
        return False

@app_commands.allowed_contexts(guilds=True, dms=False)
class E621cmds(GroupCog, group_name="e621", group_description="Get images from E621/E926"):
    """Cog for E621 commands"""
    def __init__(self, bot):
        self.bot = bot
        self.api = e6.E621(client_name="Ransas")
        self.tag_blacklist = tag_blacklist
        self.again_button = Button(label="Again", style=discord.ButtonStyle.primary, emoji="🔁")
        self.close_button = Button(label="Close", style=discord.ButtonStyle.danger, emoji="❌")

    @command(name="top", description="Gets the top posts from E621")
    async def top(self, inter: discord.Interaction, tags: str = None):
        """Gets the top post from E621"""
        try:
            await inter.response.defer()
            otags = tags
            if tags is None:
                tags = ""
            elif ", " in tags:
                tags = tags.replace(", ", " ")
            tags += " order:score"
            tags = nsfw_check(tags, inter)
            for tag in self.tag_blacklist:
                tags += f" {tag}"
            posts = self.api.posts.search(tags=tags, limit=1, page=1)
            if len(posts) == 0 or posts[0].file_obj is None:
                await inter.followup.send("No posts found with those tags", ephemeral=True)
                return
            embed = discord.Embed(title="Top post", description=f"Tags: {otags}",
                                  color=discord.Color.default(),
                                  url=f"https://e621.net/posts/{str(posts[0].id)}")
            embed.add_field(name="Score", value=f"{posts[0].score.up + posts[0].score.down} "
                            f"(↑{posts[0].score.up} ↓{str(posts[0].score.down).strip('-')})")
            embed.add_field(name="Rating", value=posts[0].rating, inline=False)
            embed.set_footer(text=f"Command ran by {str(inter.user)} | Ransas",
                             icon_url=f"{inter.user.display_avatar.url}")
            embed.set_image(url=posts[0].file_obj.url)
            await inter.followup.send(embed=embed, ephemeral=True)
        except Forbidden as e:
            await inter.followup.send(f"An error occurred: {e}", ephemeral=True)
            traceback.print_exc()

    @command(name="random", description="Get a random post from e621")
    async def random(self, inter: discord.Interaction, tags: str = None):
        """Gets a random post from E621"""
        async def r_callback(inter: discord.Interaction):
            """Callback for the again button"""
            if inter.user.id == inter.message.interaction_metadata.user.id:
                post = random.choice(self.api.posts.search(tags=tags))
                embed = discord.Embed(title="Random post", description=f"Tags: {otags}",
                                      color=discord.Color.default(),
                                      url=f"https://e621.net/posts/{str(post.id)}")
                embed.add_field(name="Score", value=f"{post.score.up + post.score.down} "
                                f"(↑{post.score.up} ↓{str(post.score.down).strip('-')})")
                embed.add_field(name="Rating", value=post.rating)
                embed.set_footer(text=f"Command ran by {str(inter.user)} | Ransas",
                                 icon_url=f"{inter.user.display_avatar.url}")
                embed.set_image(url=post.file_obj.url)
                await inter.response.edit_message(embed=embed, view=view)
                return True
            else:
                await inter.response.send_message("You can't use this button", ephemeral=True)
                return False

        await inter.response.defer()
        otags = tags
        if tags is None:
            tags = ""
        elif ", " in tags:
            tags = tags.replace(", ", " ")
        for tag in self.tag_blacklist:
            tags += f" {tag}"
        tags = nsfw_check(tags, inter)
        posts = self.api.posts.search(tags=tags)
        try:
            post = random.choice(posts)
        except IndexError:
            await inter.followup.send("No posts found with those tags", ephemeral=True)
            return
        if len(posts) == 0 or post.file_obj is None:
            await inter.followup.send("No posts found with those tags", ephemeral=True)
            return
        embed = discord.Embed(title="Random post", description=f"Tags: {otags}",
                              color=discord.Color.default(),
                              url=f"https://e621.net/posts/{str(post.id)}")
        embed.add_field(name="Score", value=f"{post.score.up + post.score.down} "
                        f"(↑{post.score.up} ↓{str(post.score.down).strip('-')})")
        embed.add_field(name="Rating", value=post.rating)
        embed.set_footer(text=f"Command ran by {str(inter.user)} | Ransas",
                         icon_url=f"{inter.user.display_avatar.url}")
        embed.set_image(url=post.file_obj.url)
        view = View()
        view.add_item(self.again_button)
        view.add_item(self.close_button)
        self.again_button.callback = r_callback
        self.close_button.callback = close_callback
        await inter.followup.send(embed=embed, ephemeral=True, view=view)

    @command(name="gif", description="Get a random gif from e621")
    async def gif(self, inter: discord.Interaction, tags: str = None):
        """Gets a random gif from E621"""
        async def g_callback(inter: discord.Interaction):
            """Callback for the again button"""
            if inter.user.id == inter.message.interaction_metadata.user.id:
                post = random.choice(self.api.posts.search(tags=tags))
                if len(posts) == 0 or posts[0].file_obj is None:
                    return False
                embed = discord.Embed(title="Random gif", description=f"Tags: {otags}",
                                      color=discord.Color.default(),
                                      url=f"https://e621.net/posts/{str(post.id)}")
                embed.add_field(name="Score", value=f"{post.score.up + post.score.down} "
                               f"(↑{post.score.up} ↓{str(post.score.down).strip('-')})")
                embed.add_field(name="Rating", value=post.rating)
                embed.set_footer(text=f"Command ran by {str(inter.user)} | Ransas",
                                 icon_url=f"{inter.user.display_avatar.url}")
                embed.set_image(url=post.file_obj.url)
                await inter.response.edit_message(embed=embed, view=view)
                return True
            else:
                await inter.response.send_message("You can't use this button", ephemeral=True)
                return False

        await inter.response.defer()
        otags = tags
        if tags is None:
            tags = ""
        elif ", " in tags:
            tags = tags.replace(", ", " ")
        tags += " animated"
        for tag in self.tag_blacklist:
            tags += f" {tag}"
        tags = nsfw_check(tags, inter)
        posts = self.api.posts.search(tags=tags)
        try:
            post = random.choice(posts)
        except IndexError:
            await inter.followup.send("No posts found with those tags", ephemeral=True)
            return
        if len(posts) == 0 or post.file_obj is None:
            await inter.followup.send("No posts found with those tags", ephemeral=True)
            return
        embed = discord.Embed(title="Random gif", description=f"Tags: {otags}",
                              color=discord.Color.default(),
                              url=f"https://e621.net/posts/{str(post.id)}")
        embed.add_field(name="Score", value=f"{post.score.up + post.score.down} "
                         f"(↑{post.score.up} ↓{str(post.score.down).strip('-')})")
        embed.add_field(name="Rating", value=post.rating)
        embed.set_footer(text=f"Command ran by {str(inter.user)} | Ransas",
                         icon_url=f"{inter.user.display_avatar.url}")
        embed.set_image(url=post.file_obj.url)
        view = View()
        view.add_item(self.close_button)
        view.add_item(self.again_button)
        self.close_button.callback = close_callback
        self.again_button.callback = g_callback
        await inter.followup.send(embed=embed, ephemeral=True, view=view)


async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(E621cmds(bot))
