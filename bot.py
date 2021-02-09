import os
import csv
import random
import tempfile
from dotenv import load_dotenv
from tabulate import tabulate
#from datetime import datetime
import asyncio
import discord
#from discord import message
#from discord import client
from discord.ext import commands
from sqlalchemy.sql.expression import null
#from discord.ext.commands.errors import CommandInvokeError

#from sqlalchemy.sql.elements import Null
#from sqlalchemy.sql.expression import false, true

from db import *


# --- Bot Config and Constants---
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='pp!', description='Pen Pen', intents=intents)

EMOJIS = {
    'eye': '\U0001F441',
    'dice': '\U0001F3B2',
    'speaker': '\U0001F50A'
}


#--- Authorization definition ---
def is_allowed():
    async def __check_role(ctx):
        org_id = 744370996148174890
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.permissions.administrator == True or role.id == org_id:
                return True
        return False

    return commands.check(__check_role)


# --- Commands ---
@bot.command(aliases=['info'])
async def list_commands(ctx):
    embed=discord.Embed(
        title="Lista de comandos",
        color=0x3385ff
        )
    dict_list = {
        'roll': """
            Rollea una serie entre los usuarios del Canal de Voz al que estas unido. Reaccionando con {} se lanza un nuevo roll, mientras que reaccionando \
            con {} marca la serie como vista (limite de 60 segundos para ambas aciones).
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
        """.format(EMOJIS["dice"], EMOJIS["eye"]),
        'rr': "*(roll reaction)* Similar al comando roll, pero entre todas las series sin ver",
        'ldb': "*(list database)* Muestra las series disponibles para ver, el usuario que propuso cada serie, sus tickets correspondientes y la fecha en que salió (o no).",
        'lw, lwatched': "*(list watched)* Muestra las series ya vistas",
        'lnw, lnwatched': "*(list not watched)* Muestra las series no vistas",
        'lda': "*(list adoptables)* Imprime la base de datos de las series adoptables, aka con 5 tickets.",
        'add, aefu': """
            *(add entry for user)* Agrega una serie a la lista.
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
            *Ejemplo: add @Tensz Baccano!*
            """,
        'chd': """
            *(change view date)* Cambia la fecha de visto de una serie. El valor serie y fecha tienen que encontrarse \
            entre comillas dobles o simples, y la fecha en formato DD-MM-YYYY.
            *Ejemplo: chd "Nazo No Kanojo X" "23-01-2020"*
            """,
        'remove': """
            Borra una entrada por **nombre** de la base de datos.
            *Ejemplo: remove Boku no Pico"*
            """,
        'adopt': """
            Adopta una serie entre las disponibles en *lda*, mantiniendo sus tickets. Es necesario tener un rol con jerarquía correspondiente.
            *Ejemplo: adopt @Bravelycold Ishuzoku Reviewers*
            """,
        'tick': """
            Suma un ticket a todas las series no vistas en la base de datos. Esta acción no se puede deshacer.
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
            """
    }
    for k, v in dict_list.items():
        embed.add_field(name=k, value=v, inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=['on?'])
async def atiendo_virgos(ctx):
    await ctx.send("Atiendo virgos. No ves que atiendo virgos?")

# - Lists -
async def order_entries_by_date():
    pass

async def table_of_entries(entries):
    table = []
    for entry in entries:
        table.append([
            bot.get_user(entry.user_id).name,
            entry.entry_name,
            entry.tickets,
            entry.view_date.strftime("%d %b %Y") if entry.view_date != None else ' '
        ])
    
    return tabulate(table, headers=[
        "Autor",
        "Serie",
        "Tickets",
        "Fecha visto"
    ])

async def send_text_as_attachment(ctx, string, filename="Output.txt"):
    with tempfile.NamedTemporaryFile("w") as temp:
        temp.writelines(string)
        temp.flush()
        await ctx.send(
            "El mensaje supera los 2000 caracteres. Adjuntando como archivo de texto",
            file=discord.File(temp.name, filename=filename)
        )

@bot.command(aliases=['ldb'])
async def list_db(ctx):
    entries = get_all_entries()
    if len(entries) == 0:
        return await ctx.send("No hay series propuestas")

    table = await table_of_entries(entries)
    output = "Lista completa de series\n```{}```".format(table)

    if len(output) > 2000:
        await send_text_as_attachment(ctx, table, filename="Lista de series.txt")
    else:
        await ctx.send(output)

@bot.command(aliases=['lda'])
async def list_adopt(ctx):
    entries = get_5_ticks()
    if len(entries) == 0:
        return await ctx.send("No hay series para adoptar")
    
    table = await table_of_entries(entries)
    output = "Lista de series para adoptar\n```{}```".format(table)

    if len(output) > 2000:
        await send_text_as_attachment(ctx, table, filename="Lista de series.txt")
    else:
        await ctx.send(output)

@bot.command(aliases=['lwatched', 'lw'])
async def list_watched(ctx):
    entries = get_viewed_entries()
    if len(entries) == 0:
        return await ctx.send("No hay series vistas")

    table = await table_of_entries(entries)
    output = "Lista de series vistas\n```{}```".format(table)

    if len(output) > 2000:
        await send_text_as_attachment(ctx, table, filename="Lista de series.txt")
    else:
        await ctx.send(output)

@bot.command(aliases=['lnwatched', 'lnw'])
async def list_not_watched(ctx):
    entries = get_not_viewed_entries()
    if len(entries) == 0:
        return await ctx.send("No hay series sin ver")

    table = await table_of_entries(entries)
    output = "Lista de series sin ver\n```{}```".format(table)

    if len(output) > 2000:
        await send_text_as_attachment(ctx, table, filename="Lista de series.txt")
    else:
        await ctx.send(output)


# - Rolls -
@bot.command(name='roll_reaction', aliases=['rr'])
@is_allowed()
async def roll_reaction(ctx, entries=Null):
    def check_emoji(reaction, user):
        return user == ctx.message.author and (
            str(reaction.emoji) == EMOJIS['eye'] or str(reaction.emoji) == EMOJIS['dice']
        )
    
    if entries == Null:
        entries = get_not_viewed_entries()

    end_loop = False
    while end_loop == False:
        try:
            roll = random.randint(0,len(entries)-1)
            entry = entries[roll]
        except:
            return await ctx.send("No hay series para ver!")

        member = ctx.guild.get_member(entry.user_id)

        m = await ctx.send("**{}** propuesta por **{}**. Prepará el pochoclo que salio tu serie!".format(
            entry.entry_name,
            member.display_name
        ))
        for e in ["eye", "dice"]:
            await m.add_reaction(EMOJIS[e])
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=120, check=check_emoji)
            if m.id == reaction.message.id:
                if reaction.emoji == EMOJIS["dice"]:
                    continue
                elif reaction.emoji == EMOJIS["eye"]:
                    m = await change_view_date(ctx, entry.entry_name)
                    await m.add_reaction(EMOJIS["dice"])
                    try:
                        reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check_emoji)
                        if m.id == reaction.message.id and reaction.emoji == EMOJIS["dice"]:
                            continue
                    except asyncio.TimeoutError:
                        await m.clear_reactions()
        except asyncio.TimeoutError:
            await m.clear_reactions()

        end_loop = True


@bot.command(name='roll_vc_reaction', aliases=['roll'])
@is_allowed()
async def roll_vc_reaction(ctx):
    entries = []
    try:
        vc = discord.utils.get(ctx.guild.voice_channels, id=ctx.author.voice.channel.id)
        vc_users = vc.members
        for u in vc_users:
            for entr in get_entries_from_user(u.id):
                if entr.view_date == None:
                    entries.append(entr)
    except AttributeError:
        return await ctx.send("Debes ingresar a un canal de voz para poder ejecutar este comando")

    await roll_reaction(ctx, entries)


# - DB modifiers -
@bot.command(aliases=['aefu', 'add'])
@is_allowed()
async def add_entry_for_user(ctx, user: discord.Member, *, entry:str):
    old_entry = get_entry_from_name(entry)
    if old_entry != None:
        return await ctx.send("Serie ya propuesta por **{}**".format(
            bot.get_user(old_entry.user_id).name
        ))
    for e in get_entries_from_user(user.id):
        if e.view_date == None:
            return await ctx.send("{} tiene para ver **{}**".format(
                user.name,
                e.entry_name
            ))  
            
    add_entry(user.id, entry)
    await ctx.send("Se agregó la serie!")


@bot.command(aliases=['chd'])
@is_allowed()
async def change_view_date(ctx, entry:str, new_date:str=Null):
    set_date_to_entry(entry, new_date)
    entry = get_entry_from_name(entry)
    return await ctx.send("Serie **{}** marcada como vista el {}".format(
        entry.entry_name,
        entry.view_date.strftime("%d-%m-%Y")
    ))


@bot.command(aliases=['tick'])
@is_allowed()
async def add_tickets(ctx):
    increment_tickets()
    return await ctx.send("tickets agregados!")


@bot.command(aliases=['adopt'])
@is_allowed()
async def act_adopt(ctx, user: discord.Member, *, entry:str):
    adoptable = get_5_ticks()
    nombres = []
    for serie in adoptable:
        nombres.append(serie.entry_name.lower())
    for entr in get_entries_from_user(user.id):
        if entr.view_date == None:
            await ctx.send("Usuario ya tiene una propuesta activa, primero borrarla e intentar de nuevo")  
            return
    if not(entry.lower() in nombres):
        await ctx.send('Esta serie no es adoptable')
        return
    change_user_id_to_entry(entry, user.id)
    await ctx.send("Se agregó la serie")


@bot.command(aliases=['remove'])
@is_allowed()
async def delete_entry(ctx, *, entry:str):
    if get_entry_from_name(entry) == None:
        await ctx.send("Entrada inexistente")
        return
    remove_entry(get_entry_from_name(entry))
    await ctx.send('Entrada borrada ')
    return


@bot.command(aliases=['icsv'])
@is_allowed()
async def import_csv(ctx, filename='import.csv', delimiter=';'):
    try:
        csv_file = open(filename)
        csv_records = csv.reader(csv_file, delimiter=delimiter)
    except FileNotFoundError:
        return await ctx.send("El archivo {} no existe".format(filename))
 
    for row in csv_records:
        # Remove @ from username (if any) and get member info
        user_name = row[0].lstrip('@')
        member = ctx.guild.get_member_named(user_name)

        try:
            add_entry(
                member.id,
                row[1],
                row[2]
            )
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'id'":
                await ctx.send('No se pudo agregar la entrada ya que el usuario "{}" no existe.'.format(user_name))
                continue
            else:
                return await ctx.send("Error desconocido: {}".format(e))

        await ctx.send("Agregada entrada **{}** de **{}**".format(
            row[1],
            member.display_name
        ))
        
    await ctx.send("**Importación finalizada!**")


# - Error handling -
@roll_reaction.error
@roll_vc_reaction.error
@act_adopt.error
async def permission_error(ctx, error):
    if error.__class__== commands.errors.CheckFailure:
        await ctx.send("No tenes permisos para ejecutar este comando")
    print(error.__class__ , error)


@add_entry_for_user.error
async def add_entry_for_user_error(ctx, error):
    if error.__class__ == commands.MissingRequiredArgument:
        await ctx.send("Faltan argumentos '{}'".format(error.param))
        return
    if error.__class__ == commands.BadArgument:
        await ctx.send("Error en argumento {}".format(str(error)))
        return
    if error.__class__ == commands.MemberNotFound:
        await ctx.send("Usuario no encontrado: {}".format(str(error)))
        return
    print(error.__class__ ,error)


bot.run(token)
