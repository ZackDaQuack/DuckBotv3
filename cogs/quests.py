import discord
import configparser
import ast
from discord.ext import commands
from modules.duckLog import logger
from modules.duckDB import DuckDB
from storage.lists import china_solgan
from random import randint
from datetime import datetime, timedelta

#############################################
#    Rip your eyes, this code sucks         #
#         quests.py [07/04/24]              #
#      Made on July 4th RAWWWWWWWW          #
#############################################

config = configparser.ConfigParser()
config.read("config.ini")

guild_id = [int(config.get("GENERAL", "allowed_guild"))]
quest_cooldown = int(config.get("CREDITS", "quest_cooldown"))

db = DuckDB()

quests = {
    1: "Send {} messages",
    2: "Reply to {} messages",
    3: "React to {} messages",
    4: "Send {} images",
    5: "Chat with **Quack** {} times.",
    6: "React to messages with a **duck emoji** {} times.",
}


def gen_quest_data(num_quests=3):
    sl_quests = []

    for _ in range(num_quests):
        selection = randint(1, len(quests))

        found = False
        for quest in sl_quests:
            if quest[0] == selection:
                quest[1] += randint(1, 5)
                found = True
                break

        if not found:
            sl_quests.append([selection, randint(1, 5)])

    return sl_quests


def pretty_quests(data):
    return [quests[quest_id].format(quest_count) for quest_id, quest_count in data]


async def gen_quest_embed(user_quests):
    desc = ""
    for i in pretty_quests(user_quests):
        desc += f"- {i}\n"

    embed = discord.Embed(title=await china_solgan(), description=desc, color=0x27F25D)
    embed.set_thumbnail(url="https://media1.tenor.com/m/h0ush348TR8AAAAC/woah-instagram.gif")
    return embed


def get_cooldown_time(quest_data):
    try:
        if isinstance(quest_data[-1], (int, float)):
            cooldown_timestamp = float(quest_data[-1])
            return datetime.fromtimestamp(cooldown_timestamp)
        else:
            return None
    except (IndexError, ValueError):
        return None


def is_on_cooldown(quest_data):
    cooldown_end = get_cooldown_time(quest_data)
    if cooldown_end:
        return datetime.now() < cooldown_end
    return False


class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("[QUESTS]   Initialized")

    quest_cmd = discord.SlashCommandGroup("quest", "Quest commands")

    async def handle_quest(self, quest_id, user):
        db_quests = await db.get_quest_data(user.id)
        if db_quests:
            user_data = ast.literal_eval(db_quests)

            if user_data and all(isinstance(quest, list) and len(quest) == 2 for quest in user_data):
                for i, (q_id, q_count) in enumerate(user_data):
                    if q_id == quest_id:
                        user_data[i] = [q_id, max(0, q_count - 1)]
                        if user_data[i][1] == 0:
                            user_data.pop(i)

                        if all(q_count == 0 for _, q_count in user_data):
                            cooldown_timestamp = (datetime.now() + timedelta(seconds=quest_cooldown)).timestamp()
                            user_data.append(cooldown_timestamp)

                            embed = discord.Embed(
                                title="+ 300 Social Credits",
                                description="You finished your quest and gained 300 credits!",
                                color=0x27F25D,
                            )
                            embed.set_thumbnail(
                                url="https://media1.tenor.com/m/6JJwUMO_zkwAAAAd/social-credit-troll.gif"
                            )
                            await db.add_credits(user.id, 300)
                            await user.send(embed=embed)
                            logger.info(f"[QUESTS] {user.name} finished their quest")
                        await db.set_quest_data(user.id, str(user_data))
                        break

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.embeds or message.attachments:
            await self.handle_quest(4, message.author)

        if message.reference:
            await self.handle_quest(2, message.author)
        else:
            await self.handle_quest(1, message.author)

        if self.bot.user.mentioned_in(message):
            await self.handle_quest(5, message.author)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if str(payload.emoji) == "🦆":
            await self.handle_quest(6, member)
        await self.handle_quest(3, member)

    @quest_cmd.command(name="status", description="View the status on your quest", guild_ids=guild_id)
    async def status(self, ctx):
        user_id = ctx.author.id
        db_quests = await db.get_quest_data(user_id)

        if db_quests:
            logger.info(f"[QUESTS] {ctx.user.name} checked their quest status")

            user_data = ast.literal_eval(db_quests)

            if is_on_cooldown(user_data):

                cooldown_end = get_cooldown_time(user_data)
                timestamp = int(cooldown_end.timestamp())
                discord_timestamp = f"<t:{timestamp}:R>"

                await ctx.respond(f"You can get new quests {discord_timestamp}", ephemeral=True)

            elif user_data and all(isinstance(quest, list) and len(quest) == 2 for quest in user_data):
                embed = await gen_quest_embed(user_data)
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                await ctx.respond("You don't have any active quests!", ephemeral=True)
        else:
            await ctx.respond("You don't have any active quests!", ephemeral=True)

    @quest_cmd.command(name="get", description="Get new quests", guild_ids=guild_id)
    async def getquest(self, ctx):
        user_id = ctx.author.id

        await db.ensure_user(ctx.author.id)
        db_quests = await db.get_quest_data(user_id)

        if db_quests != "":
            user_data = ast.literal_eval(db_quests)
            if is_on_cooldown(user_data):

                cooldown_end = get_cooldown_time(user_data)
                timestamp = int(cooldown_end.timestamp())
                discord_timestamp = f"<t:{timestamp}:R>"

                return await ctx.respond(f"You can get new quests {discord_timestamp}", ephemeral=True)

            if user_data and all(isinstance(quest, list) and len(quest) == 2 for quest in user_data):
                return await ctx.respond("You already have an active quest!", ephemeral=True)

        new_quests = gen_quest_data()
        await db.ensure_user(user_id)
        await db.set_quest_data(user_id, str(new_quests))

        embed = await gen_quest_embed(new_quests)

        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.respond("Couldn't dm you a copy! Make sure your dms are open!", embed=embed, ephemeral=True)
        else:
            await ctx.respond("A copy has been dmed to you.", embed=embed, ephemeral=True)

        logger.info(f"[QUESTS] Quest generated for {ctx.user.name}")


def setup(bot):
    bot.add_cog(Quests(bot))
