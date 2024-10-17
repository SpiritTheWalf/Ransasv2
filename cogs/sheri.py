"""Cog for fetching images and videos from the Sheri API"""
import json
import os
import discord
import aiohttp

from aiohttp import ClientConnectionError
from aiohttp.web_exceptions import HTTPUnauthorized
from dotenv import load_dotenv
from discord.ext.commands import GroupCog
from discord.app_commands import command
from discord.ext import commands

load_dotenv()

with open("utils/endpoints.json", encoding="utf-8") as file:
    endpoints = json.load(file)

sfw_endpoints = endpoints['SFW_ENDPOINTS']
nsfw_endpoints = endpoints['NSFW_ENDPOINTS']


class InvalidEndpointError(ValueError):
    """Error that is called if an invalid endpoint is passed"""


class UnauthorizedError(HTTPUnauthorized):
    """Error that is called if you do not have a valid API key"""
    def __init__(self, message="Unauthorized, please make sure your API key is correct"):
        self.message = message
        super().__init__(reason=message)


headers = {"Authorization": f"Token {os.getenv('API_KEY')}",
              "User-Agent": "RansasV2/1.0 (Python AIOHTTP) Coded by SpiritTheWalf" }


def extract_numbers(url):
    """Extract numbers from a URL"""
    parts = url.rstrip("/").split("/")
    if parts[-1].isdigit():
        return parts[-1]
    return None

async def fetch_from_api(endpoint, count):
    """Fetch images or videos from the Sheri API"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"https://sheri.bot/api/{endpoint}?count={count}",
                               headers=headers) as response:
            if response.status == 200:
                data = await response.json()

                if isinstance(data, dict):
                    data = [data]

                if not isinstance(data, list):
                    return

                messages = []

                if endpoint == "videos":
                    # Handle video messages as plain text
                    for video in data:
                        if isinstance(video, dict):
                            video_url = video.get("url")
                            report_url = video.get("report_url")
                            author = video.get("author", {})
                            artist_name = author.get("name", "Unknown")
                            artist_link = author.get("link", "#")
                            video_id = extract_numbers(report_url)
                            footer_text = f"ID: {video_id} | Powered by the Sheri API"
                            artist_text = f"[🎨 Artist: {artist_name}]({artist_link})"
                            direct_url_text = f"[🌐 Direct URL to video]({video_url})"
                            report_text = f"[Report to the Sheri Devs]({report_url})"

                            # Construct plain text message
                            message_content = f"{direct_url_text}\n{artist_text}"
                            f"\n{report_text}\n{footer_text}"
                            messages.append(message_content)
                else:
                    # Handle non-video messages as embeds
                    invalid_items = []
                    for image in data:
                        if isinstance(image, dict):
                            image_url = image.get("url")
                            report_url = image.get("report_url")
                            author = image.get("author", {})
                            artist_name = author.get("name", "Unknown")
                            artist_link = author.get("link", "#")
                            image_id = extract_numbers(report_url)
                            footer_text = f"ID: {image_id} | Powered by the Sheri API"
                            artist_text = f"[🎨 Artist: {artist_name}]({artist_link})"
                            direct_url_text = f"[🌐 Direct URL to image]({image_url})"
                            report_text = f"[Report to the Sheri Devs]({report_url})"

                            # Construct embed
                            embed = discord.Embed(title=f"{endpoint}")
                            embed.set_image(url=image_url)
                            embed.add_field(name="", value=f"{direct_url_text}"
                            f"\n{artist_text}\n{report_text}")
                            embed.set_footer(text=footer_text)
                            messages.append(embed)
                        else:
                            invalid_items.append(image)

                if messages:
                    return messages
                elif invalid_items:
                    raise ValueError(f"Invalid items: {invalid_items}")
                else:
                    raise ValueError("No items found")

            elif response.status == 401:
                print(headers)
                raise UnauthorizedError()
            else:
                raise ClientConnectionError("API request failed with status code"
                f"{response.status}")


class Sheri(GroupCog, group_name="sheri", group_description="sheri related commands"):
    """Cog for fetching images and videos from the Sheri API"""
    def __init__(self, bot):
        self.bot = bot

    @command(name="image", description="Get an image or video from the Sheri API")
    async def image(self, inter: discord.Interaction, endpoint: str, count: int = 1):
        """Get an image or video from the Sheri API"""
        if endpoint not in sfw_endpoints and endpoint not in nsfw_endpoints:
            raise InvalidEndpointError

        if endpoint in nsfw_endpoints and not inter.channel.is_nsfw():
            await inter.response.send_message("This is an NSFW endpoint,"
            "please use this command in an NSFW channel", ephemeral=True)
            raise commands.NSFWChannelRequired(inter.channel)

        # Fetch messages (either embeds or plain text)
        messages = await fetch_from_api(endpoint, count)

        # Send each message (embed or plain text)
        for message in messages:
            if isinstance(message, discord.Embed):
                await inter.response.send_message(embed=message)
            else:
                await inter.response.send_message(content=message)


async def setup(bot):
    """Setup the Sheri Cog"""
    await bot.add_cog(Sheri(bot))
