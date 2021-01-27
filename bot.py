import asyncio
import discord
from discord import message
from discord import client
from discord.ext import commands
from datetime import datetime
import random

from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import false, true

from db import add_entry, get_all_entries, increment_tickets, remove_entry, get_entry_from_name, get_entry_from_user, get_viewed_entries, set_date_to_entry, get_5_ticks, change_user_id_to_entry


import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!!', description='entrys', intents=intents)

EMOJIS = {
    'thumbs_up': '\U0001F44D',
    'eye': '\U0001F441',
    'dice': '\U0001F3B2'
}

def is_org():
    async def __check_role(ctx):
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.id == 744370996148174890:
                return True
        return False
    return commands.check(__check_role)

def is_admin():
    async def __check_role(ctx):
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.permissions.administrator == True:
                return True
        return False
    return commands.check(__check_role)


@bot.command(name='roll')
async def roll(ctx):
    entries = len(get_all_entries())
    if entries == 0:
        await ctx.send("No hay entradas")
        return
    roll = random.randint(0,entries-1)
    entry = get_all_entries()[roll]
    await ctx.send("{} propuesta por <@{}>".format(entry.entry_name, entry.user_id))
    member = ctx.guild.get_member(entry.user_id)
    if member.voice != None:
        await ctx.send(
                 "Parece que <@{}> está conectade a {}, así que prepará el pochoclo que salio tu serie".format(
                    entry.user_id, member.voice.channel
                    ))
        remove_entry(entry)
        return
    await ctx.send("Parece que <@{}> no esta en vc...".format(
        entry.user_id
        ))


@bot.command(name='roll_reaction', aliases=['rc'])
async def roll_reaction(ctx):
    entries = get_all_entries()
    entries_count = len(entries)

    def check_emoji(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in EMOJIS.values()

    if entries_count == 0:
        m = await ctx.send("No hay entradas")
        return

    end_loop = False
    while end_loop == False:
        roll = random.randint(0,entries_count-1)
        entry = entries[roll]
        member = ctx.guild.get_member(entry.user_id)
     
        text = "**{}** propuesta por <@{}>.\n".format(entry.entry_name, entry.user_id)
        if member.voice != None:
            text += "Se encuentra en vc {}. Prepará el pochoclo que salio tu serie!".format(member.voice.channel)

            m = await ctx.send(text)
            await m.add_reaction(EMOJIS["eye"])
            await m.add_reaction(EMOJIS["dice"])
            #remove_entry(entry)
        else:
            text += "Parece que <@{}> no esta en vc...".format(entry.user_id)

            m = await ctx.send(text)
            await m.add_reaction(EMOJIS["dice"])
        
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check_emoji)
            if m.id == reaction.message.id:
                if reaction.emoji == EMOJIS["dice"]:
                    continue
                elif reaction.emoji == EMOJIS["eye"]:
                    await change_view_date(ctx, entry.entry_name)
                    break
        except asyncio.TimeoutError:
            pass

        end_loop = True


#@bot.command()
#async def add(ctx, entry: str):
#    if get_entry_from_user(ctx.message.author.id) != None:
#        await ctx.send("eh loco vos ya propusiste")
#        return
#    if get_entry_from_name(entry.lower()) != None:
#            await ctx.send("esa serie esta repetida")
#            return
#    add_entry(ctx.author.id, entry)
#    await ctx.send("Se agregó la serie :picardia:")


@bot.command(aliases=['aefu', 'add'])
async def add_entry_for_user(ctx, user: discord.Member, *, entry:str):
    if get_entry_from_user(user.id) != None:
        await ctx.send("Usuario ya tiene una propuesta")
        return
    exs_entry = get_entry_from_name(entry.lower())
    if exs_entry != None:
        await ctx.send(
            "Esa serie esta repetida, fue propuesta por @{}".format(
                bot.get_user(exs_entry.user_id)
                ))
        return
    add_entry(user.id, entry)
    await ctx.send("Se agregó la serie :picardia:")


@add_entry_for_user.error
async def add_entry_for_user_error(ctx, error):
    if error.__class__ == commands.MissingRequiredArgument:
        await ctx.send("Faltan argumentos chinchu '{}'".format(error.param))
        return
    if error.__class__ == commands.BadArgument:
        await ctx.send("Pifiaste en algun argumento... {}".format(str(error)))
        return
    if error.__class__ == commands.MemberNotFound:
        await ctx.send("No encontre al user".format(str(error)))
        return
    print(error.__class__ ,error)

@bot.command(aliases=['chd'])
async def change_view_date(ctx, entry:str, new_date:str=Null):
    set_date_to_entry(entry, new_date)
    entry = get_entry_from_name(entry)
    await ctx.send("Serie **{}** marcada como vista el {}".format(
        entry.entry_name,
        entry.view_date.strftime("%d-%m-%Y")
    ))
    return


@bot.command(aliases=['ldb'])
#@is_admin()
async def list_db(ctx):
    embed=discord.Embed(
        title="Lista de series propuestas y sus autores",
        color=0xFF5733
        )
    formated_list = ""
    entries = get_all_entries()
    if len(entries) == 0:
        await ctx.send("No hay entradas")
        return
    for entry in entries:
        formated_list += "**{}** - {} - {} ticket(s)\n".format(
            bot.get_user(entry.user_id),
            entry.entry_name,
            entry.tickets
            )
    embed.add_field(name="\u200b", value=formated_list)
    await ctx.send(embed=embed)


@list_db.error
async def list_db_error(ctx, error):
    if error.__class__== commands.errors.CheckFailure:
        await ctx.send("No tenes permisos, que hacias queriendo toquetear?")
    print(error.__class__ , error)

@bot.command(aliases=['lwatched', 'lwch'])
#@is_admin()
async def list_watcheds(ctx):
    embed=discord.Embed(
        title="Lista de series vistas",
        color=0x85C1E9
        )
    formated_list = ""
    entries = get_viewed_entries()
    if len(entries) == 0:
        await ctx.send("No hay entradas")
        return
    for entry in entries:
        formated_list += "**{}** - {} - {}\n".format(
            entry.entry_name,
            entry.view_date.strftime("%d %b %Y"),
            bot.get_user(entry.user_id)
            )
    embed.add_field(name="\u200b", value=formated_list)
    await ctx.send(embed=embed)

@bot.command(aliases=['vchk'])
async def is_in_voice(ctx, user: discord.User):
    print(ctx.guild.get_member(user.id))
    member = ctx.guild.get_member(user.id)
    if member.voice != None:
        await ctx.send("El usuario mencionado esta en el canal {}!".format(member.voice.channel))
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
            await list_db(ctx) 
            return
    await ctx.send("Privilegios insuficientes")

@bot.command(aliases=['info'])
async def list_commands(ctx):
    embed=discord.Embed(
        title="Lista de comandos",
        color=0x3385ff
        )
    dict_list = {
        'roll': """
            Rollea entre las series propuestas. Reaccionando con {} se lanza un nuevo roll, mientras que reaccionando \
            con {} marca la serie como vista (limite de 60 segundos para ambas aciones).
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
        """.format(EMOJIS["dice"], EMOJIS["eye"]),
        'chd': """
            *(change view date)* Cambia la fecha de visto de una serie. El valor serie y fecha tienen que encontrarse \
            entre comillas dobles o simples, y la fecha en formato DD-MM-YYYY.
            *Ejemplo: chd "Nazo No Kanojo X" "23-01-2020"*
            """,
        'add, aefu': """
            *(add entry for user)* Agrega una serie a la lista.
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
            *Ejemplo: add @Tensz Baccano!*
            """,
        'ldb': "*(list database)* Muestra las series disponibles para ver, el usuario que propuso cada serie y sus tickets correspondientes.",
        'lwch': "*(list watcheds)* Muestra las series ya vistas",
        'lda': "*(list adoptables)* Imprime la base de datos de las series adoptables, aka con 5 tickets.",
        'adopt': """
            'Adopta' una serie entre las disponibles en lda y mantiene sus tickets. Es necesario tener un rol con jerarquía correspondiente.",
            Ejemplo: adopt @BravelyCold Ishuzoku Reviewers*
            """,
        'tick': """
            suma un ticket a todas las series no vistas en la base de datos. Esta acción no se puede deshacer.
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
            """
    }
    for k, v in dict_list.items():
        embed.add_field(name=k, value=v, inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=['lda'])
async def list_adopt(ctx):
    #lo siguiente es codigo copiado de ldb pero solo las series con 5 tickets
    adoptable = get_5_ticks()
    embed=discord.Embed(
    title="Lista de series adoptables",
    color=0xebae34
    )
    formated_list = ""
    entries = adoptable
    if len(entries) == 0:
        await ctx.send("No hay series adoptables")
        return
    for entry in entries:
        formated_list += "**{}** - {} - {} ticket(s)\n".format(
            bot.get_user(entry.user_id),
            entry.entry_name,
            entry.tickets
            )
    embed.add_field(name="\u200b", value=formated_list)
    await ctx.send(embed=embed)

@bot.command(aliases=['adopt'])
#@is_admin()
async def act_adopt(ctx, user: discord.Member, *, entry:str):
    adoptable = get_5_ticks()
    nombres = []
    for serie in adoptable:
        nombres.append(serie.entry_name.lower())
    if get_entry_from_user(user.id) != None:
        await ctx.send("Usuario ya tiene una propuesta, primero borrarla e intentar de nuevo")
        return
    print(nombres)
    if not(entry.lower() in nombres):
        await ctx.send('Esta serie no es adoptable')
        return
    change_user_id_to_entry(entry, user.id)
    await ctx.send("Se agregó la serie :picardia:")


bot.run(token)
