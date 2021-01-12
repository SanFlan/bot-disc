import discord
from discord.ext import commands
import random

from db import add_entry, get_all_entries, increment_tickets, remove_entry, get_entry_from_name, get_entry_from_user

import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!?', description='entrys', intents=intents)

@bot.command(name='roll')
async def roll(ctx):
    entries = len(get_all_entries())
    if entries == 0:
        await ctx.send("No hay entradas")
        return
    roll = random.randint(0,entries-1)
    entry = get_all_entries()[roll]
    await ctx.send("{} propuesta por <@{}>".format(entry.entry_name, entry.user_id))
    try:
        member = ctx.guild.get_member(entry.user_id)
        if member.voice != None:
            await ctx.send(
                    "Preparate el pochoclo <@{}> que salio tu serie".format(
                        entry.user_id
                        ))
            remove_entry(entry)
            return
        await ctx.send("Parece que <@{}> no esta en vc...".format(
            entry.user_id
            ))
    except Exception as e:
        await ctx.send("Hubo un error y me hice caca encima {}".format(e))
        return

@bot.command()
<<<<<<< HEAD
async def add(ctx, entry: str):
    if get_entry_from_user(ctx.message.author.id) != None:
        await ctx.send("eh loco vos ya propusiste")
        return
    if get_entry_from_name(entry.lower()) != None:
            await ctx.send("esa serie esta repetida")
            return

#    for entry in get_all_entries():
#        if ctx.message.author.id == entry.user_id:
#            await ctx.send("eh loco vos ya propusiste")
#            return
#        if entry.lower == entry.entry_name.lower:
#            await ctx.send("esa serie esta repetida")
#            return
    add_entry(ctx.author.id, entry)
    await ctx.send("Se Agrego La Entry!")
=======
async def add(ctx, new_entry: str):
    for db_entry in get_all_entries():
        if ctx.message.author.id == new_entry.user_id:
            await ctx.send("eh loco vos ya propusiste")
            return
        if new_entry.lower() == (db_entry.entry_name).lower(): 
            await ctx.send("esa serie esta repetida")
            return
    add_entry(ctx.author.id, new_entry)
    await ctx.send("Serie Agregada!")
>>>>>>> 9145955b22cc2fb70aeb5b573caa4bc8f97ad5a4


@bot.command(aliases=['ldb'])
async def list_db(ctx):
    entries = get_all_entries()
    if len(entries) == 0:
        await ctx.send("No hay entradas")
        return
    for entry in entries:
        await ctx.send(entry.entry_name)
        await ctx.send("propuesto por {}".format(bot.get_user(entry.user_id)))


@bot.command(aliases=['vchk'])
async def is_in_voice(ctx, user: discord.User):
    print(ctx.guild.get_member(user.id))
    member = ctx.guild.get_member(user.id)
    if member.voice != None:
        await ctx.send("El usuario mencionado esta en voice!")
        return
    await ctx.send("El usuario mencionado no esta en voice :(")
    return


@bot.command(aliases=['tick'])
#@commands.has_role('el mas pijudo')
#asi funciona bien, queria ver como hacer para que mandara un mensaje de error pero no lo descubri
async def tickets(ctx):
    for role in ctx.author.roles:
        if str(role) == 'el mas pijudo':
            increment_tickets()
            await ctx.send("Sumando tickets... beep boop...")
            return
    await ctx.send("Privilegios insuficientes")


bot.run(token)
