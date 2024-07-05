import aiohttp
import discord
import configparser
import json
from discord.ext import commands, tasks
from modules.duckLog import logger
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.ini")

guild_id = [int(config.get("GENERAL", "allowed_guild"))]
status_channel = int(config.get("STATUS", "channel"))
scan_time = int(config.get("STATUS", "scan_time"))

with open("storage/status.json", "r") as stats:
    rblx_info = json.load(stats)


async def update_json(to_edit, new):
    with open("storage/status.json", "r") as load1:
        loaded_config = json.load(load1)
    loaded_config[to_edit] = new
    with open("storage/status.json", "w") as load2:
        json.dump(loaded_config, load2, indent=4)


async def roblox_version():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://clientsettingscdn.roblox.com/v2/client-version/MacPlayer") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['clientVersionUpload']
                else:
                    logger.error("Failed to fetch Roblox version! (status error)")
                    return False
    except aiohttp.ClientError:
        logger.error("Failed to fetch Roblox version! (no wifi)")
        return False


class Command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.oldRobloxVersion = rblx_info.get("oldversion")
        self.bot.currentRobloxVersion = rblx_info.get("version")
        self.bot.shoutMessage = rblx_info.get("shout_message")
        self.bot.isUp = rblx_info.get("macsploit_updated")
        self.version_checker.start()
        logger.info("[STATUS]   Initialized")

    async def edit_status(self, to_set):
        channel = await self.bot.fetch_channel(status_channel)

        message = None
        async for msg in channel.history(limit=10):
            if msg.author == self.bot.user and msg.embeds:
                message = msg
                break

        if to_set == "down":
            embed = discord.Embed(
                title="Roblox Has Updated",
                description=(
                    f"Since Roblox updated, MacSploit won't work.\n\n"
                    f"Old version: {self.bot.oldRobloxVersion}\n"
                    f"New version: {self.bot.currentRobloxVersion}"
                ),
                color=0xf90202
            )
        else:
            embed = discord.Embed(
                title="MacSploit is Up",
                description=(
                    f"MacSploit has been updated to {self.bot.currentRobloxVersion}\n\n"
                    f"Please open a ticket if you are having issues."
                ),
                color=0x06df23
            )

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/icons/1188161972500443208/"
                "f7b63c2383dbcb2c21cce3b06b172b4d.webp?size=240"
        )
        embed.set_footer(
            text=f"Data updated on {datetime.now().strftime('%Y-%m-%d at %#I:%M %p')} (CT)",
            icon_url="https://png.pngtree.com/png-vector/20190118/ourlarge/pngtree-vector-clock-icon-png"
                     "-image_323861.jpg"
        )
        if self.bot.shoutMessage:
            embed.add_field(name="Important Message:", value=self.bot.shoutMessage)

        if message:
            await message.edit(embed=embed)
        else:
            await channel.send(embed=embed)

    @tasks.loop(seconds=scan_time)
    async def version_checker(self):
        scan_version = await roblox_version()
        if scan_version != self.bot.currentRobloxVersion and scan_version:
            logger.info("[STATUS] Roblox update detected!")

            self.bot.oldRobloxVersion = self.bot.currentRobloxVersion
            self.bot.currentRobloxVersion = scan_version
            await update_json("version", self.bot.currentRobloxVersion)
            await update_json("oldversion", self.bot.oldRobloxVersion)

            self.bot.isUp = False
            await update_json("macsploit_updated", False)

            self.bot.shoutMessage = ""
            await update_json("shout_message", "")

            await self.edit_status("down")
        else:
            await self.edit_status("up") if self.bot.isUp else await self.edit_status("down")

    @discord.slash_command(name="status", description="Sets the status", guild_ids=guild_id)
    async def set_status(self, ctx, to_set: bool, important_message: str = ""):
        if to_set:
            self.bot.isUp = True
            await update_json("macsploit_updated", True)
        else:
            self.bot.isUp = False
            await update_json("macsploit_updated", False)

        self.bot.shoutMessage = important_message
        await update_json("shout_message", important_message)

        await self.edit_status("up" if to_set else "down")
        await ctx.respond(f"Set status to {to_set}", ephemeral=True)
        logger.info(f"[STATUS] Status changed to {to_set} via the command")


def setup(bot):
    bot.add_cog(Command(bot))
