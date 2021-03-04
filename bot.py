import os
import discord
from os import path
from discord.ext import commands

# --- Bot Config and Constants---
if path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
else:
    token = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', description='Pen Pen', intents=intents)

# -- Main --
@bot.event
async def on_ready():
    print('Bot is online')

# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)