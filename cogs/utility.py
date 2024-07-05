import discord
import configparser
import aiohttp
from discord.ext import commands
from modules.duckLog import logger
from storage.lists import generate_propaganda
from modules.duckDB import DuckDB
from random import randint

#  We need more fun commands :fire:  #

config = configparser.ConfigParser()
config.read("config.ini")

guild_id = [int(config.get("GENERAL", "allowed_guild"))]
pixabay_api = config.get("KEYS", "pixabay")
master = int(config.get("GENERAL", "master_duck"))
dm_channel = int(config.get("AI", "dm_channel"))

db = DuckDB()


async def duck():
    params = {
        "key": pixabay_api,
        "q": "duck",
        "image_type": "animals",
        "safesearch": "true",
        "order": "popular",
        "page": randint(1, 2),
        "per_page": 100,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://pixabay.com/api/", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                random_index = randint(0, len(data['hits']) - 1)
                return data['hits'][random_index]['largeImageURL']
            else:
                logger.error("Error fetching pixabay image!")
                return None


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        logger.info("[UTILITY]  Initialized")

    db_cmd = discord.SlashCommandGroup("db", "Database commands")

    @discord.slash_command(name="fact", description="Generate a random fact about a user.")
    async def fact(self, ctx, user: discord.User):
        await ctx.respond(await generate_propaganda(f"<@{user.id}>"))
        logger.info("[CMD] Random fact given")

    @discord.slash_command(name="duck", description="Quack!")
    async def duck(self, ctx):
        image = await duck()
        if image is not None:
            embed = discord.Embed(
                title="Quack!",
                description="Here is your duck image...",
                color=0x2a8105,
            )
            embed.set_image(url=image)
            await ctx.respond(embed=embed)
            logger.info("[CMD] Duck image sent")
        else:
            await ctx.respond("Sorry! Your duck image couldn't be retrieved! *sad quack*")

    @discord.slash_command(name="say", description="Make the duck quack!", guild_ids=guild_id)
    async def say(self, ctx, message: str):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("Quack! You need to be an admin to run this!", ephemeral=True)

        await ctx.respond("Done!", ephemeral=True)
        channel = await self.bot.fetch_channel(ctx.channel.id)
        await channel.send(message)
        logger.warning(f"[CMD] {ctx.user.name} made the bot say \"{message}\"")

    @discord.slash_command(name="dm", description="Send a...personal dm.....", guild_ids=guild_id)
    async def dm(self, ctx, user: discord.User, message: str):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("Quack! You need to be an admin to run this!", ephemeral=True)

        try:
            await user.send(message)
        except discord.Forbidden:
            await ctx.respond("Failed to dm. User probably blocked the bot.", ephemeral=True)
        else:
            await ctx.respond("Done", ephemeral=True)

        logger.warning(f"[SAY] {ctx.user.name} made the bot dm \"{message}\" to {user.name}")

    @db_cmd.command(name="delete_user", description="Remove a user from the database", guild_ids=guild_id)
    async def delete_user(self, ctx, user: discord.User):

        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        if await db.delete_user(user.id):
            await ctx.respond("Operation Successful!", ephemeral=True)
        else:
            await ctx.respond("Operation Failed! User dosn't exist.", ephemeral=True)

    @db_cmd.command(name="get_user_data", description="Gets everything known about a user", guild_ids=guild_id)
    async def get_user_data(self, ctx, user: discord.User):

        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        if not await db.user_exists(user.id):
            return await ctx.respond("User dosn't exist in the database.", ephemeral=True)

        user_crd = await db.get_credits(user.id)
        user_quests = await db.get_quest_data(user.id)

        await ctx.respond(f"**UserID:** {user.id}\n**Credits:** {user_crd}\n**Quests:** {user_quests}", ephemeral=True)

    # Guild enforcer
    async def validate_guild(self, guild):
        if guild.id not in guild_id:
            await guild.leave()
            logger.info(f"[MAIN] Left invalid server. id: {guild.id}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.validate_guild(guild)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.validate_guild(guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.channel.DMChannel) and message.author.id != self.bot.user.id:
            embed = discord.Embed(
                title=f"{message.author.name} ({message.author.id})",
                description=message.content,
                color=0x272727
            )
            channel = await self.bot.fetch_channel(dm_channel)
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
