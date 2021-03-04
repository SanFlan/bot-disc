import discord
import csv
import io
from discord.ext import commands
from db import *

class CSV(commands.Cog):
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

    @commands.command(aliases=['icsv'])
    async def import_csv(self, ctx, filename='import.csv', delimiter=';'):
        async def get_discord_user(user):
            # Remove @ from username (if any) and return member info
            u = user.lstrip('@')
            if u.isdigit():
                return ctx.guild.get_member(int(u))
            elif ctx.guild.get_member_named(u):
                return ctx.guild.get_member_named(u)
            else:
                return None
        async def string_to_date(date_text):
            # Check if date is formated properly and return a datetime object, or return None
            try:
                return datetime.strptime(date_text, '%d-%m-%y').date()
            except ValueError:
                return None

        try:
            csv_file = open(filename)
            csv_records = csv.reader(csv_file, delimiter=delimiter)
        except FileNotFoundError:
            return await ctx.send("El archivo {} no existe".format(filename))
    
        for row in csv_records:
            member = await get_discord_user(row[0])
            entry_name = row[1]
            tickets = row[2]
            entry_date = await string_to_date(row[3])
        
            try:
                add_entry(
                    member.id,
                    entry_name,
                    tickets,
                    entry_date
                )
            except AttributeError as e:
                if str(e) == "'NoneType' object has no attribute 'id'":
                    await ctx.send('No se pudo agregar la entrada ya que el usuario "{}" no existe.'.format(row[0]))
                    continue
                else:
                    return await ctx.send("Error desconocido al agregar la entrada: {}".format(e))

            await ctx.send("Agregada entrada **{}** de **{}**".format(
                entry_name,
                member.display_name
            ))

        await ctx.send("**Importación finalizada!**")

    @commands.command(aliases=['ecsv'])
    async def export_csv(self, ctx, delimiter=';'):
        f = io.StringIO()
        writer = csv.writer(f, delimiter=delimiter)
        for entry in get_all_entries():
            writer.writerow([
                entry.user_id,
                entry.entry_name,
                entry.tickets,
                entry.view_date.strftime("%d-%m-%y") if entry.view_date != None else ' '
            ])
        f.seek(0)
        await ctx.send(file=discord.File(f, filename="Lista_series.csv"))
        f.close()


def setup(bot):
    bot.add_cog(CSV(bot))