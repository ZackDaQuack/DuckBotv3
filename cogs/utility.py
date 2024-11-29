"""

File: utlilty.py
Author: ZackDaQuack
Last Edited: 11/28/2024

Info:

This module contains the utility / fun commands
Also handles guild validation and forwarding dms to staff channel

Slash Commands:
    /duck: Grabs a random duck image from Pixabay
    /say <msg>: Sends a message to the channel.
    /annoy <target> <amount>: Mass pings a user
    /dm <user> <message>: Sends a direct message to a user.
    /delete_user <user>: Deletes a user from duckDB
    /get_user_data <user>: Retrieves user data from duckDB
    /ping: Checks the bot's latency.
    /smite: "Smites" a user. (Basically a timeout)
    /shutdown: Shuts down the bot.

Prefix Command:
    execute <python_script>: Executes a Python script. (be very careful, this will run ANYTHING on your computer)

"""

import asyncio
import contextlib
import io
import os
import random
import time
from datetime import timedelta

import matplotlib.pyplot as plt
import psutil
import traceback
import discord
import configparser
import aiohttp
from discord.ext import commands
from modules.duckLog import logger
from storage.lists import generate_propaganda
from modules.duckDB import DuckDB
from random import randint, shuffle, sample

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


class ShutdownModel(discord.ui.Modal):
    stupid_words = ["sigma", "balls", "gay", "esex", "quack", "alpha", "beta", "lmfao"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.confirmation_code = " ".join(sample(self.stupid_words, 3))
        self.add_item(discord.ui.InputText(label=f"Type: {self.confirmation_code}"))

    async def callback(self, interaction: discord.Interaction):
        if self.children[0].value.lower() == self.confirmation_code:
            logger.info(f"[MAIN] {interaction.user.name} shutdown the bot.")
            await interaction.response.send_message("Goodbye!")
            await interaction.client.close()  # duck murderer
        else:
            await interaction.response.send_message("Incorrect confirmation code.", ephemeral=True)


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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

    @discord.slash_command(name="annoy", description="Be annoying", guild_ids=guild_id)
    async def annoy(self, ctx, target: discord.User, amount: int):
        if ctx.author.id == 893131404437762058 or ctx.author.id == 717854704335585281 or ctx.author.id == 773306136685183006:
            logger.warning(f"[CMD] {ctx.author.name} annoying {target.name} {amount} times.")

            if amount > 200:
                return await ctx.respond("no.", ephemeral=True)

            await ctx.defer()

            accessible_channels = [channel for channel in ctx.guild.text_channels if
                                   channel.permissions_for(target).send_messages and
                                   channel.permissions_for(ctx.guild.me).send_messages]

            if not accessible_channels:
                return await ctx.respond("Quack! There are no channels I can send messages to.", ephemeral=True)

            shuffle(accessible_channels)
            channel_cycle = accessible_channels * (amount // len(accessible_channels) + 1)

            stop_flag = False

            async def stop_annoy(interaction):
                nonlocal stop_flag
                if interaction.user == ctx.author:
                    stop_flag = True
                    await interaction.response.send_message("Stopping", ephemeral=True)
                else:
                    await interaction.response.send_message("You can't stop this!", ephemeral=True)

            stop_button = discord.ui.Button(label="Stop", style=discord.ButtonStyle.red)
            stop_button.callback = stop_annoy
            view = discord.ui.View()
            view.add_item(stop_button)

            response_message = await ctx.respond(f"Sending pings... 0/{amount}", view=view)

            for i in range(amount):
                if stop_flag:
                    break

                try:
                    await channel_cycle[i].send(target.mention, delete_after=0.1)
                    await response_message.edit(content=f"Sending pings... {i + 1}/{amount}")
                    await asyncio.sleep(.5)
                except discord.Forbidden:
                    await ctx.respond(
                        f"Quack! Couldn't send a message to {channel_cycle[i].mention}. "
                        f"I don't have permission there!",
                        ephemeral=True)

            if stop_flag:
                await response_message.edit(content="Quack!", view=None)
            else:
                await response_message.edit(content="Quack Quack!", view=None)

        else:
            return await ctx.respond("Quack! You need to be a master admin for this!", ephemeral=True)

    # Sends a dm to a user, splits it into 1500 character chunks.
    @discord.slash_command(name="dm", description="Send a...personal dm.....", guild_ids=guild_id)
    async def dm(self, ctx: discord.ApplicationContext, user: discord.User, message: str):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("Quack! You need to be an admin to run this!", ephemeral=True)

        await ctx.defer(ephemeral=True)

        try:
            chunks = []
            current_chunk = ""
            for word in message.split():
                next_chunk = current_chunk + " " + word
                if len(next_chunk) < 1500:
                    current_chunk = next_chunk
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = word
            if current_chunk:
                chunks.append(current_chunk.strip())

            for chunk in chunks:
                await user.send(chunk)

        except discord.Forbidden:
            await ctx.respond("Failed to dm. User probably blocked the bot.", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}", ephemeral=True)
            logger.warning(f"[DM] Error sending DM: {e}")
        else:
            await ctx.respond("Done", ephemeral=True)
            logger.warning(f"[DM] {ctx.author.name} made the bot dm "
                           f"\"{message if len(message) < 50 else '[LONG MESSAGE]'}\" to {user.name}")

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

    # Stupid over the top ping command (yes, this is all matplotlib is used for)
    @commands.slash_command(name="ping", description="Get the bot's ping (with a graph!)", guild_ids=guild_id)
    async def ping(self, ctx):
        cmd_start = time.time()
        await ctx.defer()
        logger.info(f"[CMD] Generating ping info for {ctx.user.name}")

        try:
            def calculate_rate(start, end):
                diff = end - start
                return diff / 1 if diff > 0 else 0

            def format_bytes(size_bytes):
                if size_bytes >= (1024 ** 3):
                    return f"{round(size_bytes / (1024 ** 3), 2)} GB"
                else:
                    return f"{round(size_bytes / (1024 ** 2), 2)} MB"

            # System Info
            latency = round(self.bot.latency * 1000)
            db_latency = round(await db.get_latency(), 3)
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent(interval=1)
            memory_info = process.memory_info()
            rss_memory = format_bytes(memory_info.rss)
            vms_memory = format_bytes(memory_info.vms)
            threads = process.num_threads()
            swap = psutil.swap_memory()

            # Network Info
            net_io_start = psutil.net_io_counters()
            await asyncio.sleep(1)
            net_io_end = psutil.net_io_counters()
            net_sent_rate = calculate_rate(net_io_start.bytes_sent, net_io_end.bytes_sent)
            net_recv_rate = calculate_rate(net_io_start.bytes_recv, net_io_end.bytes_recv)

            # Uselss Infomation
            meaningless_number = random.randint(1, 1000000)
            useless_fact = random.choice([
                "The sky is blue.",
                "Elephants are gray.",
                "This command is pointless.",
                "Water is wet.",
                "Fire is hot.",
                "Grass is green.",
                "The Earth is flat.",
                "Time keeps ticking.",
                "Chickens can't fly (much).",
                "Bananas are yellow.",
                "Cats say meow.",
                "Zero times anything is zero.",
                "Oxygen is necessary for breathing.",
                "Snow is cold.",
                "The moon is not made of cheese.",
                "Penguins can't type.",
                "Fish live in water.",
                "Your nose is on your face.",
                "This fact list is too long.",
                "The Titanic did not have seatbelts."
            ])

            # Graph Generation
            data = [latency, db_latency, cpu_percent, memory_info.rss / (1024 ** 2),
                    threads, net_sent_rate / 1024, net_recv_rate / 1024, swap.percent]
            labels = ["Bot Latency", "DB Latency", "CPU Usage", "RSS Memory", "Threads",
                      "Net Sent", "Net Recv", "Swap"]
            plt.figure(figsize=(14, 8))

            # Mess up the graph
            colors = [plt.cm.gist_ncar(random.random()) for _ in range(len(labels))]
            plt.bar(labels, data, color=colors, width=random.uniform(0.5, 1.5))
            plt.xticks(rotation=random.randint(-90, 90), fontsize=random.randint(8, 18))
            plt.yticks(fontsize=random.randint(8, 18), color=random.choice(["red", "blue", "green", "yellow"]))
            plt.title("TOP SECRET DUCK GRAPH", fontsize=random.randint(16, 30), fontweight="bold", color="green")

            # Add stupid annotations
            for i, value in enumerate(data):
                plt.text(i, value + random.uniform(0, 10), f"{value:.2f}", fontsize=random.randint(10, 14),
                         rotation=random.randint(-45, 45), color=random.choice(colors), ha="center")

            # Add fake visual clutter
            for _ in range(random.randint(5, 15)):
                plt.plot(random.sample(range(len(labels)), 2),
                         [random.uniform(min(data), max(data)) for _ in range(2)],
                         linestyle=random.choice(['-', '--', '-.', ':']),
                         linewidth=random.uniform(0.5, 3),
                         color=random.choice(["pink", "cyan", "lime", "orange"]))

            # Mess up the grid
            plt.grid(axis='y', linestyle=random.choice(['--', '-.', ':']), alpha=random.uniform(0.3, 1.0),
                     color=random.choice(["gray", "black"]))

            # Hide some spines for no reason
            plt.gca().spines['top'].set_visible(random.choice([True, False]))
            plt.gca().spines['right'].set_visible(random.choice([True, False]))
            plt.tight_layout()

            # Save the graph
            with io.BytesIO() as img_buffer:
                plt.savefig(img_buffer, format='PNG')
                img_buffer.seek(0)
                file = discord.File(img_buffer, filename="system_metrics.png")

            plt.close()

            # Create Embed
            embed = discord.Embed(title="Pong! 🦆", color=0x45b702)
            embed.add_field(name="Bot Latency", value=f"`{latency}ms`{' (nice)' if latency == 69 else ''}", inline=True)
            embed.add_field(name="DB Latency", value=f"`{db_latency}ms`", inline=True)
            embed.add_field(name="CPU Usage", value=f"`{cpu_percent:.1f}%`", inline=True)
            embed.add_field(name="RSS Memory", value=f"`{rss_memory}`", inline=True)
            embed.add_field(name="VMS Memory", value=f"`{vms_memory}`", inline=True)
            embed.add_field(name="Threads", value=f"`{threads}`", inline=True)
            embed.add_field(name="Network Sent/s", value=f"`{net_sent_rate / 1024:.2f} KB`", inline=True)
            embed.add_field(name="Network Received/s", value=f"`{net_recv_rate / 1024:.2f} KB`", inline=True)
            embed.add_field(name="Swap Usage", value=f"`{swap.percent:.1f}%`", inline=True)
            embed.add_field(name="Generation Time", value=f"`{round(time.time() - cmd_start, 2)}` Seconds", inline=True)
            embed.add_field(name="Number", value=f"`{meaningless_number}`", inline=True)
            embed.add_field(name="Did you know?", value=useless_fact, inline=True)
            embed.set_image(url="attachment://system_metrics.png")

            await ctx.respond(embed=embed, file=file)

        except Exception as e:
            await ctx.respond(f"Error: {e}")

    @discord.slash_command(name="shutdown", description="Emergency shutdown. Stops everything", guild_ids=guild_id)
    async def shutdown(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("❤️ But it refused.", ephemeral=True)

        modal = ShutdownModel(title="Emergency Shutdown")
        await ctx.send_modal(modal)

    # Smite people
    @discord.slash_command(name="smite", description="Smite a user", guild_ids=guild_id)
    async def smite(self, ctx, user: discord.User, duration: int, name: str = "Smitten Peasant"):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("Quack! You need to be an admin to run this!", ephemeral=True)

        await ctx.defer()

        original_name = user.display_name

        await user.timeout_for(timedelta(seconds=duration))
        await user.edit(nick=name)
        await ctx.respond(f"⚡ {user.mention} has been smitten by the gods! ⚡", ephemeral=True)
        await ctx.send("https://tenor.com/view/bird-lightning-strike-tragedy-fried-gif-2022815810689047932")
        await asyncio.create_task(self.revert_nickname(user, duration, original_name))

    async def revert_nickname(self, user: discord.User, duration: int, original_name: str):
        await asyncio.sleep(duration)
        try:
            await user.edit(nick=original_name)
        except discord.Forbidden:
            logger.error(f"[CMD] Couldn't revert nickname for {user.id} due to missing permissions.")

    # Remote code execution :shocked:
    @commands.command(name="execute")
    async def execute(self, ctx, *, python: str):
        if ctx.author.id != master:
            return

        local_vars = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(compile(python, "<string>", "exec"), local_vars)

            output = stdout.getvalue()
            if output:
                await ctx.reply(f"```py\n{output}\n```")
            else:
                await ctx.reply("Code executed successfully (no output).")

        except Exception:
            error_message = f"```py\n{traceback.format_exc()}\n```"
            if len(error_message) > 2000:
                error_message = f"```py\n{traceback.format_exc()[-1997:]}\n```"
            await ctx.reply(error_message)

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
