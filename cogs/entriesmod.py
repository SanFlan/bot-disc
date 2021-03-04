import discord
from discord.ext import commands
from db import *

class EntriesMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        org_id = 745289656215797840
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.permissions.administrator == True or role.id == org_id:
                return True
        return False

    async def cog_command_error(self, ctx, error):
        # Prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return
        
        if isinstance(error, commands.CheckFailure):
            return await ctx.send('No tenes permisos suficientes para ejecutar este comando')
        
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('Error - falta argumento requerido.')
        if isinstance(error, commands.MemberNotFound):
            return await ctx.send('El nombre de usuario **{}** no es correcto.'.format(error.argument))
        if isinstance(error, commands.BadArgument):
            return await ctx.send('Error - Argumento **{}** no es correcto.'.format(error.argument))
        if isinstance(error, commands.CommandInvokeError):
            return await ctx.send("Error - La serie no se encuentra en la base de datos")
        
        await ctx.send('Error desconocido - Mensaje de error: **{}**'.format(error))

    @commands.command(aliases=['aefu', 'add'])
    async def add_entry_for_user(self, ctx, user: discord.Member, *, entry:str):
        old_entry = get_entry_from_name(entry)
        if old_entry != None:
            return await ctx.send("Serie ya propuesta por **{}**".format(
                self.get_user(old_entry.user_id).name
            ))
        for e in get_entries_from_user(user.id):
            if e.view_date == None:
                return await ctx.send("{} tiene para ver **{}**".format(
                    user.name,
                    e.entry_name
                ))  
        add_entry(user.id, entry)
        await ctx.send("Se agregó la serie!")

    @commands.command(aliases=['chd'])
    async def change_view_date(self, ctx, entry:str, new_date:str=None):
        set_date_to_entry(entry, new_date)
        entry = get_entry_from_name(entry)
        return await ctx.send("Serie **{}** marcada como vista el {}".format(
            entry.entry_name,
            entry.view_date.strftime("%d-%m-%Y")
        ))            

    @commands.command(aliases=['chticks'])
    async def change_tickets(self, ctx, entry:str, tickets:int):
        if (tickets > 5 or tickets < 1):
            return await ctx.send('El numero de tickets debe ser de 1 a 5')
        set_ticks_to_entry(entry, tickets)
        return await ctx.send("Tickets modificados!")

    @commands.command(aliases=['tick'])
    async def add_tickets(self, ctx, tickets = 1):
        increment_tickets(tickets)
        return await ctx.send('Tickets agregados!')

    @commands.command(aliases=['adopt'])
    async def act_adopt(self, ctx, user: discord.Member, *, entry:str):
        adoptable = get_5_ticks()
        nombres = []
        for serie in adoptable:
            nombres.append(serie.entry_name.lower())
        for entr in get_entries_from_user(user.id):
            if entr.view_date == None:
                return await ctx.send('El Usuario **{}** no puede adoptar la serie ya que tiene para ver **{}**'.format(
                    user.display_name,
                    entr.entry_name
                ))  
        if not(entry.lower() in nombres):
            await ctx.send('Esta serie no es adoptable')
            return
        change_user_id_to_entry(entry, user.id)
        await ctx.send("Se agregó la serie")

    @commands.command(aliases=['remove'])
    async def delete_entry(self, ctx, *, entry:str):
        remove_entry(get_entry_from_name(entry))
        return await ctx.send('Entrada borrada ')


def setup(bot):
    bot.add_cog(EntriesMod(bot))