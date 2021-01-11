import discord
from discord.ext import commands
import random

import os
from dotenv import load_dotenv


class Entry:
    def __init__(self, user, entry, ticket):
        self.user = user
        self.entry = entry
        self.ticket = 0

    def __str__(self):
        return 'userid: {} entry: {} tickets: {}'.format(
                self.user,
                self.entry,
                self.ticket
                )


db = []

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?!', description='entrys', intents=intents)

@bot.command(name='roll')
async def roll(ctx):
    entries = len(db)
    if entries == 0:
        await ctx.send("No hay entradas")
        return
    roll = random.randint(0,entries-1)
    entry = db[roll]
    await ctx.send("{} propuesta por <@{}>".format(entry.entry, entry.user))
    try:
        member = ctx.guild.get_member(entry.user)
        if(member.voice != None):
            await ctx.send("Preparate el pochoclo <@{}> que salio tu serie".format(
                entry.user
                ))
            db.remove(entry)
            return
        await ctx.send("Parece que <@{}> no esta en vc...".format(
            entry.user
            ))
    except Exception:
        await ctx.send("Hubo un error y me hice caca encima")
        return

@bot.command()
async def add(ctx, entry: str):
    tmp = Entry(ctx.author.id, entry, 0)
    db.append(tmp)
    await ctx.send("Se Agrego La Entry!")

@bot.command(aliases=['ldb'])
async def list_db(ctx):
    for entry in db:
        print(entry)
        print("propuesta por {}".format(bot.get_user(entry.user)))
    await ctx.send("Mira los logs")

@bot.command(aliases=['vchk'])
async def is_in_voice(ctx, user: discord.User):
    print(ctx.guild.get_member(user.id))
    member = ctx.guild.get_member(user.id)
    if(member.voice != None):
        await ctx.send("El usuario mencionado esta en voice!")
        return
    await ctx.send("El usuario mencionado no esta en voice :(")
    return

bot.run(token)
