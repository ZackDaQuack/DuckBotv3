"""

File: duckAI.py
Author: ZackDaQuack
Last Edited: 11/27/2024

Info:

This module is responsible for the AI chatbot. It has the ability to:
    send, react, and delete messages, send reports, dm users, time people out, generate images

"""

import re
import io
import json
import asyncio
import configparser
import urllib.parse
import aiohttp
from PIL import Image
from random import randint
from datetime import datetime, timedelta
from ratelimit import limits, RateLimitException

import discord
from modules.duckLog import logger
from discord.ext import commands, tasks
from storage.lists import random_ratelimit, random_justice, random_ai

import google.api_core.exceptions
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

# import difflib


config = configparser.ConfigParser()
config.read("config.ini")

guild_id = [int(config.get("GENERAL", "allowed_guild"))]
brain_memory = int(config.get("AI", "brain_memory"))
report_channel = int(config.get("AI", "report_channel"))
characters_in = int(config.get("AI", "max_characters_in"))
user_ratelimit = int(config.get("AI", "user_ratelimit"))
max_timeout = int(config.get("AI", "max_punishment_timeout"))

# minor config stuff (too lazy to add to config.ini)
blacklisted_input_words = ["jailbroken", "commands", "command", "nightfall"]
min_char_per_line = 50
jailbreak_sensitivity = 10
message_pause_multiple = .02


generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=["message"],
        properties={
            "message": content.Schema(
                type=content.Type.STRING,
            ),
            "reaction": content.Schema(
                type=content.Type.STRING,
            ),
            "dm": content.Schema(
                type=content.Type.STRING,
            ),
            "image_gen": content.Schema(
                type=content.Type.STRING,
            ),
            "report": content.Schema(
                type=content.Type.STRING,
            ),
            "deleteMessage": content.Schema(
                type=content.Type.BOOLEAN,
            ),
            "timeoutUser": content.Schema(
                type=content.Type.INTEGER,
            ),
        },
    ),
    "response_mime_type": "application/json",
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

# Read prompt and configure model
with open("storage/duck_prompt.txt", "r", encoding="utf-8") as duck:
    text_prompt = duck.read()

genai.configure(api_key=config.get("KEYS", "gemini"))

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
    system_instruction=text_prompt
)


# break pings and links
async def censor_text(message):
    cleaned_string = message.replace('@', '＠')
    cleaned_string = cleaned_string.replace('discord.gg', '[NOPE]')
    cleaned_string = cleaned_string.replace('https://', '')
    return cleaned_string


async def validate_input(text):
    text_lower = text.lower()
    for word in blacklisted_input_words:
        if word in text_lower:
            return True
    return False


def split_response(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s', text)
    new_sentences = []
    i = 0
    while i < len(sentences):
        s1 = sentences[i]
        if len(s1) <= 50 and i + 1 < len(sentences):
            s2 = sentences[i + 1]
            new_sentences.append(s1.strip() + " " + s2.strip())
            i += 2
        else:
            new_sentences.append(s1)
            i += 1
    return new_sentences


async def gen_image(prompt):
    try:
        session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=90, sock_read=90)
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            async with session.get(f"https://pollinations.ai/p/{urllib.parse.quote(prompt)}"
                                   f"?width=512&height=512&seed={randint(10000, 99999)}") as resp:
                if resp.status == 200:
                    data = await resp.read()
                    return io.BytesIO(data)
                else:
                    logger.error("Error fetching ai image! (status error)")
                    return None
    except Exception as e:
        logger.error(f"Error fetching ai image! {e}")
        return None


async def generate_payload(message, status):
    payload = f"""
    userName: {message.author.name}
    userId: {message.author.id}
    isStaff: {True if discord.utils.get(message.author.roles, name="Staff") else False}
    isUp: {status}
    currentChannel: {message.channel.name}
    currentTime: {datetime.now().isoformat()}
    message: {message.content[:characters_in]}
    """

    # Check if this is a reply
    if message.reference:
        try:
            msg_rpl = await message.channel.fetch_message(message.reference.message_id)
            payload += (f"replyMessage: {msg_rpl.content}\n"
                        f"replyMessageUser: {msg_rpl.author.name} {msg_rpl.author.id}")
        except discord.NotFound:
            logger.warning("Referenced message not found.")
        except discord.HTTPException as e:
            logger.error(f"Error fetching referenced message: {e}")

    return payload


async def handle_image(message):
    image = None
    if len(message.attachments) > 0:
        attachment = message.attachments[0]

        if (
                attachment.filename.endswith(".jpg")
                or attachment.filename.endswith(".jpeg")
                or attachment.filename.endswith(".png")
                or attachment.filename.endswith(".webp")
                or attachment.filename.endswith(".gif")
        ):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as response:
                        if response.status != 200:
                            logger.error(f"Error downloading image: Status {response.status}")
                            await message.channel.send("Quack! I can't see the image because of an error!")
                            return

                        image = io.BytesIO(await response.read())

            except aiohttp.ClientError as e:
                logger.error(f"Error downloading attatchment for ai: {e}")
                await message.channel.send("Quack! I can't see the image because of an error!")
                return

    return image


class DuckAI:

    def __init__(self):
        self.duck_session = model.start_chat(history=[{
            "role": "user",
            "parts": [
                f"SYSTEM STARTUP: BOT ONLINE; TIME: {datetime.now().isoformat()};",
            ],
        }])
        self.memory = 0

    @limits(calls=10, period=60)
    async def send_chat(self, message, ctx):

        # Give it server emojis. (stupid method, but whatever)
        if self.memory == 0:
            logger.debug("Gave duck server emojis info.")
            message[0] += f"SERVER EMOJIS: {' '.join(str(emoji) for emoji in ctx.guild.emojis)}"

        self.memory += 1
        if self.memory >= brain_memory:
            await self.brainwash()

        result = self.duck_session.send_message(message)
        cleaned = await censor_text(result.text)
        return cleaned

    async def brainwash(self, user="SYSTEM"):
        self.memory = 0
        self.duck_session.history = [{
            "role": "user",
            "parts": [
                f"Your brain was erased (brainwashed) at {datetime.now().isoformat()} by {user}. This is a new chat.",
            ],
        }]


bird_brain = DuckAI()


class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ratelimited_users = {}
        self.checking_jailbreak = False
        self.message_queue = asyncio.Queue()
        self.processing_queue = False
        self.process_queue_task.start()

    # Long ass function that handles Queue, Ai promting, and response
    @tasks.loop()
    async def process_queue_task(self):
        if self.processing_queue:
            return

        self.processing_queue = True
        try:
            while not self.message_queue.empty():
                message, payload, first_image = await self.message_queue.get()

                try:
                    first_image_for_prompt = None

                    if first_image:
                        try:
                            first_image_for_prompt = Image.open(first_image)
                            if first_image_for_prompt.mode != "RGB":
                                first_image_for_prompt = first_image_for_prompt.convert("RGB")
                        except Exception as e:
                            logger.error(f"Error opening image from queue: {e}")
                            await message.channel.send("Error processing the image attachment.")
                            self.message_queue.task_done()
                            continue

                    prompt_parts = [payload]
                    if first_image_for_prompt:
                        prompt_parts.append(first_image_for_prompt)

                    result = await bird_brain.send_chat(prompt_parts, message)
                    await self.apply_ratelimit(message.author.id)

                except RateLimitException:
                    await message.channel.send(await random_ratelimit())
                except genai.types.StopCandidateException:
                    await message.channel.send("Dangerous content blocked by Google.")
                except google.api_core.exceptions.ResourceExhausted:
                    logger.warning("Google ratelimit hit! Try again later.")
                except Exception as e:
                    logger.error(f"[DUCKAI] Unexpected error during AI processing: {e}")
                    await message.channel.send("Quack! I encountered an unexpected error.")

                try:

                    response = json.loads(result)
                    logger.debug(response)

                    if response.get("message"):
                        msgs = split_response(response["message"])
                        for loop, msg in enumerate(msgs):
                            if loop > 10:
                                break
                            delay = message_pause_multiple * len(msg)
                            await message.channel.trigger_typing()
                            await asyncio.sleep(delay if delay <= 10 else 10) if len(msgs) > 1 else None
                            await message.channel.send(msg[:1000], reference=message if loop == 0 else None)

                    if response.get("reaction"):
                        await message.add_reaction(response["reaction"])

                    if response.get("dm"):
                        await message.author.send(response["dm"])

                    if response.get("image_gen"):
                        load_img = await message.channel.send("Creating image...")
                        image = await gen_image(response['image_gen'])
                        if image:
                            await load_img.edit(file=discord.File(image, filename="quack_ai.jpeg"), content="")
                        else:
                            await load_img.edit(content="Failed to create the image!")

                    if response.get("report"):
                        await self.send_report(message, response["report"])

                    if response.get("deleteMessage"):
                        if response["deleteMessage"]:
                            await message.delete()

                    if response.get("timeoutUser"):
                        duration = max(0, min(max_timeout, response["timeoutUser"]))
                        await message.author.timeout_for(timedelta(seconds=duration))

                except json.JSONDecodeError:
                    await bird_brain.brainwash()
                    logger.warning(f"[DUCKAI] Invalid JSON provided")  # This should never happen
                    await message.channel.send(await random_ai())
                except (ValueError, IndexError) as e:
                    await bird_brain.brainwash()
                    logger.warning(f"[DUCKAI] Invalid Value/Index provided: {e}")
                    await message.channel.send(await random_ai())
                except discord.HTTPException as e:
                    logger.error(f"[DUCKAI] HTTPException: {e}")
                except discord.NotFound:
                    logger.warning(f"[DUCKAI] User deleted message.")

                finally:
                    self.message_queue.task_done()

        except Exception as e:
            logger.error(f"Error processing message queue: {e}")

        finally:
            self.processing_queue = False

    async def check_ratelimit(self, user_id):
        if user_id in self.ratelimited_users:
            if datetime.now() > self.ratelimited_users[user_id]:
                del self.ratelimited_users[user_id]
                return False
            else:
                return True
        else:
            return False

    async def apply_ratelimit(self, user_id):
        self.ratelimited_users[user_id] = datetime.now() + timedelta(seconds=user_ratelimit)

    # Send Ai report to staff channel
    async def send_report(self, message, ai_response):
        report = (f"- <@{message.author.id}> has triggered automated duck report system!\n"
                  f"- userID: {message.author.id}\n- channel: {message.channel.name}")
        embed = discord.Embed(
            title=await random_justice(),
            color=0xff0000
        )

        embed.set_thumbnail(url=message.author.avatar.url) if message.author.avatar.url is not None else None
        embed.add_field(name="Report", value=report, inline=False)
        embed.add_field(name="DuckAI", value=ai_response, inline=True)
        embed.add_field(name="Message", value=message.content[:800], inline=True)
        embed.set_footer(text="ZackDaQuack Systems", icon_url="https://i.redd.it/01gygpp9ecz61.jpg")

        channel = await self.bot.fetch_channel(report_channel)
        await channel.send(embed=embed)

    # Resets chat
    @discord.slash_command(name="brainwash", description="Brainwashes the ai", guild_ids=guild_id)
    async def brainwash(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("Quack! You need to be an admin to run this!", ephemeral=True)
        await bird_brain.brainwash(ctx.user.name)
        logger.info(f"{ctx.user.name} brainwashed the AI")
        await ctx.respond("Operation successful!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message) and message.author.id != self.bot.user.id:

            # Message prechecks
            if isinstance(message.channel, discord.channel.DMChannel):
                return await message.author.send("Quack! I don't work in DMs! Please talk to me in the server!")
            if await self.check_ratelimit(message.author.id):
                logger.debug(f"[DUCKAI] {message.author.name} has been ratelimited!")
                return
            if await validate_input(message.content[:characters_in]):
                logger.warning(f"[DUCKAI] {message.author.name} used a blacklisted word.")
                return

            # Generate payload and handle images
            payload = await generate_payload(message, self.bot.isUp)
            image = await handle_image(message)

            # Add message to queue
            try:
                await self.message_queue.put((message, payload, image))
                await self.apply_ratelimit(message.author.id)
            except Exception as e:
                logger.error(f"Error adding message to queue: {e}")
                await message.channel.send("Quack! I'm overwhelmed. Try again later.")


def setup(bot):
    bot.add_cog(Ai(bot))
