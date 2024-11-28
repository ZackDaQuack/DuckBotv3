"""

File: main.py
Author: ZackDaQuack
Last Edited: 11/27/2024


Info:

Fires up the bot and loads cog modules. (with a nice amount of lines)

"""

import time
import discord
from discord.ext import commands
import configparser
from modules.duckLog import logger
from colorama import Fore, Style


def run_bot():
    config = configparser.ConfigParser()
    config.read("config.ini")

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="duck!", intents=intents)

    @bot.event
    async def on_ready():
        print()
        logger.info("[MAIN] Quack! Bot is online.")

    cogs = ["duckAI", "utility", "credits", "quests", "status", "settings"]

    for cog in cogs:
        try:
            bot.load_extension(f"cogs.{cog}")
            print(f"{Fore.LIGHTBLUE_EX}[MAIN] Loaded cog: {cog}{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"[MAIN] Failed to load cog {cog}: {e}")

    try:
        bot.run(config.get("KEYS", "discord"))

    except discord.LoginFailure as e:
        logger.critical(f"[MAIN] Login Failure: {e}")
        return

    except Exception as e:
        logger.error(f"[MAIN] An unexpected error occurred: {e}")


if __name__ == "__main__":
    print(f"""{Fore.LIGHTYELLOW_EX}
    ______            _   ______       _         _____ 
    |  _  \          | |  | ___ \     | |       |____ |
    | | | |_   _  ___| | _| |_/ / ___ | |___   __   / /
    | | | | | | |/ __| |/ / ___ \/ _ \| __\ \ / /   \ \\
    | |/ /| |_| | (__|   <| |_/ / (_) | |_ \ V /.___/ /
    |___/  \__,_|\___|_|\_\____/ \___/ \__| \_/ \____/ 
                                   by {Fore.LIGHTGREEN_EX}ZackDaQuack{Style.RESET_ALL}            

    """)

    while True:
        run_bot()
        time.sleep(60)
