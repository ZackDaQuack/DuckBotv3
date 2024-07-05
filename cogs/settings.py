import discord
import configparser
from discord.ext import commands
from modules.duckLog import logger

config = configparser.ConfigParser()
config.read("config.ini")

master = int(config.get("GENERAL", "master_duck"))
guild_id = [int(config.get("GENERAL", "allowed_guild"))]


async def update_ini(section, varriable, value):
    cfgfile = open("config.ini", 'w')
    config.set(section, varriable, value)
    config.write(cfgfile)
    cfgfile.close()
    logger.info(f"[SETTINGS] INI file updated! Section: {section}  Varriable: {varriable}  New Value: {value}")


class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        logger.info("[SETTINGS] Initialized")

    set_cmd = discord.SlashCommandGroup("set", "Setting commands")

    @set_cmd.command(name="ai_memory", description="Memory of the duck", guild_ids=guild_id)
    async def ai_memory(self, ctx, new_value: str):
        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        await update_ini("AI", "brain_memory", new_value)
        await ctx.respond("Value updated", ephemeral=True)
   
    @set_cmd.command(name="ai_report_channel", description="Channel to send ai reports in", guild_ids=guild_id)
    async def ai_report_channel(self, ctx, new_value: str):
        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        await update_ini("AI", "report_channel", new_value)
        await ctx.respond("Value updated", ephemeral=True)

    @set_cmd.command(name="dm_channel", description="Channel to forward dms to", guild_ids=guild_id)
    async def dm_channel(self, ctx, new_value: str):
        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        await update_ini("AI", "dm_channel", new_value)
        await ctx.respond("Value updated", ephemeral=True)

    @set_cmd.command(name="max_credit_give", description="Max credits admins are allowed to give", guild_ids=guild_id)
    async def max_credit_give(self, ctx, new_value: str):
        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        await update_ini("CREDITS", "max_give", new_value)
        await ctx.respond("Value updated", ephemeral=True)

    @set_cmd.command(name="max_credit_deduct", description="Max credits admins are allowed to remove", guild_ids=guild_id)
    async def max_credit_deduct(self, ctx, new_value: str):
        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        await update_ini("CREDITS", "max_deduct", new_value)
        await ctx.respond("Value updated", ephemeral=True)

    @set_cmd.command(name="quest_cooldown", description="Cooldown after quests (seconds)", guild_ids=guild_id)
    async def quest_cooldown(self, ctx, new_value: str):
        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        await update_ini("QUESTS", "quest_cooldown", new_value)
        await ctx.respond("Value updated", ephemeral=True)

    @set_cmd.command(name="status_channel", description="Channel for Roblox status", guild_ids=guild_id)
    async def status_channel(self, ctx, new_value: str):
        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        await update_ini("STATUS", "channel", new_value)
        await ctx.respond("Value updated", ephemeral=True)

    @set_cmd.command(name="status_scan_time", description="Period to check for update", guild_ids=guild_id)
    async def status_scan_time(self, ctx, new_value: str):
        if not ctx.author.id == master:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

        await update_ini("STATUS", "scan_time", new_value)
        await ctx.respond("Value updated", ephemeral=True)


def setup(bot):
    bot.add_cog(Settings(bot))
