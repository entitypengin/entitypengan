#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os

import discord
from discord.ext import tasks

from server import keep_alive

discord_token = os.environ["DISCORD_TOKEN"]
bot_channel_id = int(os.environ["BOT_CHANNEL_ID"])

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@tasks.loop(seconds=60)
async def loop():
    now = datetime.datetime.now()
    if (now.hour, now.minute) == (15, 0):
        await client.get_channel(bot_channel_id).send("a")


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    loop.start()


@client.event
async def on_message(message: discord.Message):
    print(f"""On {message.channel}, {message.channel.guild}
{message.author}: {message.content}""")
    if message.author.bot:
        return


keep_alive()

client.run(discord_token)
