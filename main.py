import discord
from discord.ext import commands
import configparser
from modules.duckLog import logger
from colorama import Fore, Style

# Print banner with color
print(f"""\033[38;2;255;165;0m
______            _   ______       _         _____ 
|  _  \          | |  | ___ \     | |       |____ |
| | | |_   _  ___| | _| |_/ / ___ | |___   __   / /
| | | | | | |/ __| |/ / ___ \/ _ \| __\ \ / /   \ \\
| |/ /| |_| | (__|   <| |_/ / (_) | |_ \ V /.___/ /
|___/  \__,_|\___|_|\_\____/ \___/ \__| \_/ \____/ 
                               by {Fore.LIGHTGREEN_EX}ZackDaQuack            
                               
{Fore.LIGHTBLUE_EX}Modules:{Style.RESET_ALL}""")

config = configparser.ConfigParser()
config.read("config.ini")

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    logger.info("[MAIN] Quack! Bot is online.")

cogs = ["duckAI", "utility", "credits", "quests", "status", "settings"]
for cog in cogs:
    bot.load_extension(f"cogs.{cog}")

print(f"\n{Fore.LIGHTBLUE_EX}Log:{Style.RESET_ALL}")

bot.run(config.get("KEYS", "discord"))
