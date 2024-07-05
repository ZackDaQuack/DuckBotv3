import google.generativeai as genai
from better_profanity import profanity
import discord
import json
import asyncio
import configparser
from modules.duckLog import logger
from discord.ext import commands
from datetime import datetime
from ratelimit import limits, RateLimitException
from storage.lists import ratelimit_responses, random_justice, random_ai

# Maybe add more commands like slowmode.

config = configparser.ConfigParser()
config.read("config.ini")

guild_id = [int(config.get("GENERAL", "allowed_guild"))]
brain_memory = int(config.get("AI", "brain_memory"))
report_channel = int(config.get("AI", "report_channel"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
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

genai.configure(api_key=config.get("KEYS", "gemini"))
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

with open("storage/duck_prompt.txt", "r", encoding="utf-8") as duck:
    text_prompt = duck.read()

prompt = [
    {
        "role": "user",
        "parts": [
            text_prompt,
        ],
    },
    {
        "role": "model",
        "parts": [
            "Quack! I will follow these instructions exactly!",
        ],
    },
]


async def censor_text(message):
    cleaned_string = message.replace('@', '＠')
    cleaned_string = cleaned_string.replace('discord.gg', '[NOPE]')
    return profanity.censor(cleaned_string, "#")


class DuckAI:

    def __init__(self):
        self.duck_session = model.start_chat(history=prompt)
        self.memory = 0

    @limits(calls=10, period=60)
    async def send_chat(self, message):
        self.memory += 1
        if self.memory >= brain_memory:
            await self.brainwash()

        result = self.duck_session.send_message(message)
        cleaned = await censor_text(result.text)
        return cleaned

    async def brainwash(self):
        self.memory = 0
        self.duck_session.history = prompt


bird_brain = DuckAI()


class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ratelimit = 0
        logger.info("[DUCKAI]   Initialized")

    async def send_report(self, message, ai_response):
        report = (f"- <@{message.author.id}> has triggered automated duck report system!\n"
                  f"- userID: {message.author.id}\n- channel: {message.channel.name}")
        embed = discord.Embed(
            title=await random_justice(),
            color=0xff0000
        )

        embed.set_thumbnail(url=message.author.avatar.url)
        embed.add_field(name="Report", value=report, inline=False)
        embed.add_field(name="DuckAI", value=ai_response, inline=True)
        embed.add_field(name="Message", value=message.content, inline=True)
        embed.set_footer(text="ZackDaQuack Systems", icon_url="https://i.redd.it/01gygpp9ecz61.jpg")

        channel = await self.bot.fetch_channel(report_channel)
        await channel.send(embed=embed)

    @discord.slash_command(name="brainwash", description="Brainwashes the ai", guild_ids=guild_id)
    async def brainwash(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.respond("Quack! You need to be an admin to run this!", ephemeral=True)
        await bird_brain.brainwash()
        logger.info(f"{ctx.user.name} brainwashed the AI")
        await ctx.respond("Operation successful!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message) and message.author.id != self.bot.user.id:
            if isinstance(message.channel, discord.channel.DMChannel):
                return await message.author.send("Quack! I don't work in dms! Please talk to me in the server!")

            payload = f"""
                   userName: {message.author.name}
                   userId: {message.author.id}
                   isStaff: {discord.utils.get(message.author.roles, name="Staff")}
                   isUp: {self.bot.isUp}
                   currentChannel: {message.channel.name}
                   currentTime: {datetime.now().isoformat()}
                   message: {message.content}
                   """

            try:
                result = await bird_brain.send_chat(payload)
                self.ratelimit = 0
            except RateLimitException:
                if self.ratelimit == len(ratelimit_responses):
                    self.ratelimit = 0
                await message.channel.send(ratelimit_responses[self.ratelimit])
                self.ratelimit += 1
                return
            except genai.types.StopCandidateException:
                return await message.channel.send("Dangerous content blocked by Google. (lmao chill out)")

            try:
                parsed = json.loads(result)
                logger.debug(parsed)
                if parsed["message"]:
                    msgs = parsed["message"]
                    for loop, msg in enumerate(msgs):
                        if loop > 5:
                            break
                        delay = int(msg[1])
                        await message.channel.trigger_typing()
                        await message.channel.send(msg[0][:1000], reference=message if loop == 0 else None)
                        await asyncio.sleep(delay if delay <= 10 else 10) if len(msgs) > 1 else None
                if parsed["reaction"]:
                    await message.add_reaction(parsed["reaction"])
                if parsed["dm"]:
                    await message.author.send(parsed["dm"])
                if parsed["report"]:
                    await self.send_report(message, parsed["report"])

                return
            except json.JSONDecodeError:
                await bird_brain.brainwash()
                logger.warning(f"[DUCKAI] Invalid JSON provided")
                return await message.channel.send(await random_ai())
            except ValueError:
                await bird_brain.brainwash()
                logger.warning(f"[DUCKAI] Invalid LIST provided")
                return await message.channel.send(await random_ai())
            except IndexError:
                await bird_brain.brainwash()
                logger.warning(f"[DUCKAI] Invalid INDEX provided")
                return await message.channel.send(await random_ai())



def setup(bot):
    bot.add_cog(Ai(bot))
