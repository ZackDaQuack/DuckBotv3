import discord
import configparser
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from modules.duckLog import logger
from modules.duckDB import DuckDB

config = configparser.ConfigParser()
config.read("config.ini")

max_give = int(config.get("CREDITS", "max_give"))
max_deduct = int(config.get("CREDITS", "max_deduct"))
master = int(config.get("GENERAL", "master_duck"))
guild_id = [int(config.get("GENERAL", "allowed_guild"))]

db = DuckDB()


async def gen_cred_img(amount, method):
    pos = (435, 144)
    img_path = "storage/images/add_credit.jpg" if method == "+" else "storage/images/deduct_credit.jpg"

    image = Image.open(img_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("storage/ArialNova-Bold.ttf", 120)

    draw.text(pos, f"{method} {str(amount)}", fill=(255, 255, 255), font=font)

    byte_io = BytesIO()
    image.save(byte_io, format='JPEG')
    byte_io.seek(0)

    return byte_io


class Credits(commands.Cog):

    def __init__(self, bot):
        logger.info("[CREDITS]  Initialized")
        self.bot = bot

    cred_cmd = discord.SlashCommandGroup("credit", "Credit commands")

    @cred_cmd.command(name="add", description="Adds credits to a user", guild_ids=guild_id)
    async def add(self, ctx, user: discord.User, amount: int):

        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("Quack! You need to be an admin to run this!", ephemeral=True)
        if amount < 0:
            return await ctx.respond("You cannot use a negative number!", ephemeral=True)
        if ctx.user.id == user.id and ctx.author.id != master:
            return await ctx.respond("You cannot add credits to yourself, silly!")
        if amount >= max_give and ctx.author.id != master:
            return await ctx.respond(f"You cannot add this many credits! Limit is {max_give}", ephemeral=True)

        await db.ensure_user(user.id)
        await db.add_credits(user.id, amount)

        img = await gen_cred_img(amount, "+")
        file = discord.File(img, "plus_credits.jpg")
        embed = discord.Embed(
            title="Quack!",
            description=f"+{amount} social credits! Great work!",
            color=0x40d911,
        )
        embed.set_thumbnail(url="attachment://plus_credits.jpg")
        await ctx.respond(user.mention, embed=embed, file=file)

        logger.info(f"[CREDITS] {ctx.user.name} added {amount} social credits to {user.name}")

    @cred_cmd.command(name="deduct", description="Deducts credits from a user", guild_ids=guild_id)
    async def deduct(self, ctx, user: discord.User, amount: int):

        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("Quack! You need to be an admin to run this!", ephemeral=True)
        if amount < 0:
            return await ctx.respond("You cannot use a negative number!", ephemeral=True)
        if ctx.user.id == user.id and ctx.author.id != master:
            return await ctx.respond("You cannot deduct credits to yourself, silly! (why would you do this)")
        if amount >= max_deduct and ctx.author.id != master:
            return await ctx.respond(f"You cannot remove this many credits! Limit is {max_deduct}", ephemeral=True)

        await db.ensure_user(user.id)
        await db.deduct_credits(user.id, amount)

        img = await gen_cred_img(amount, "-")
        file = discord.File(img, "deduct_credits.jpg")
        embed = discord.Embed(
            title="Quack!",
            description=f"-{amount} social credits! Bad job >:O",
            color=0xd92511,
        )
        embed.set_thumbnail(url="attachment://deduct_credits.jpg")
        await ctx.respond(user.mention, embed=embed, file=file)

        logger.info(f"[CREDITS] {ctx.user.name} deducted {amount} social credits to {user.name}")

    @cred_cmd.command(name="set", description="Sets a user's credits", guild_ids=guild_id)
    async def deduct(self, ctx, user: discord.User, amount: int):

        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        if amount < 0:
            return await ctx.respond("You cannot use a negative number!", ephemeral=True)

        await db.ensure_user(user.id)
        await db.set_credits(user.id, amount)
        await ctx.respond("Operation Successful!", ephemeral=True)

        logger.info(f"[CREDITS] {ctx.user.name} set {user.name} credits to {amount}")

    @cred_cmd.command(name="check", description="Checks your or someone else's credits", guild_ids=guild_id)
    async def check(self, ctx, user: discord.User = None):
        own = False
        if user is None:
            user = ctx.user
            own = True

        amount = await db.get_credits(user.id)
        amount = 0 if amount is None else amount
        embed = discord.Embed(
            title=">:O" if amount <= 0 else ":)",
            description=f"{'You' if own else user.name} {'have' if own else 'has'} {amount} "
                        f"{'credit' if amount == 1 else 'credits'}!",
            color=0xd92511 if amount <= 0 else 0x40d911,
        )
        await ctx.respond(embed=embed)

        logger.info(f"[CREDITS] {ctx.user.name} checked their social credits ({amount})")

    @cred_cmd.command(name="leaderboard", description="Checks leaderboard rankings", guild_ids=guild_id)
    async def leaderboard(self, ctx, target_user: discord.User = None):
        own = False
        if target_user is None:
            target_user = ctx.user
            own = True

        top_10, target_user_rank, target_user_credits = await db.leaderboard(target_user.id)

        desc = ""
        if top_10:
            desc += "**Top 10:**\n"
            for user_data in top_10:
                user_id, user_credits, rank = user_data

                rank_suffix = "th"
                if rank == 1:
                    rank_suffix = "st"
                elif rank == 2:
                    rank_suffix = "nd"
                elif rank == 3:
                    rank_suffix = "rd"

                if rank <= 3:
                    emoji = ["🏆", "🥈", "🥉"][rank - 1]
                else:
                    emoji = "🏅"

                if user_id == target_user.id:
                    desc += f"- {emoji} **{rank}{rank_suffix}: <@{user_id}>: {user_credits} credits**\n"
                else:
                    desc += f"- {emoji} {rank}{rank_suffix}: <@{user_id}>: {user_credits} credits\n"

        user_display = "You are" if own else f"<@{target_user.id}> is"
        if target_user_rank is not None:
            desc += f"\n**{user_display} #{target_user_rank} with {target_user_credits} credits!**"
        else:
            desc += f"\n{user_display} is not ranked on the leaderboard."

        embed = discord.Embed(
            title="Social Credit Leaderboard",
            description=desc,
            color=0x20bdb7
        )
        embed.set_thumbnail(url="https://media.tenor.com/GVbLnw73qD8AAAAj/dancing-duck-karlo.gif")
        await ctx.respond(embed=embed)

        logger.info(f"[CREDITS] Leaderboard generated for {ctx.user.name}")


def setup(bot):
    bot.add_cog(Credits(bot))
