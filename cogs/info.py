import discord
from discord.ext import commands

EMOJIS = {
    'eye': '\U0001F441',
    'dice': '\U0001F3B2',
}

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['info'])
    async def list_commands(self, ctx):
        embed=discord.Embed(
            title="Lista de comandos",
            color=0x3385ff
            )
        dict_list = {
            'roll, rvc': """
                Rollea una serie entre los usuarios del Canal de Voz al que estas unido. Reaccionando al {} lanza un nuevo roll, reaccionando \
                al {} marca la serie como vista (limite de 60 segundos para ambas aciones).
                Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
            """.format(EMOJIS["dice"], EMOJIS["eye"]),
            'rall': "*(roll all)* Similar al comando roll, pero entre todas las series sin ver",
            'ldb': "*(list database)* Muestra las series disponibles para ver, el usuario que propuso cada serie, sus tickets correspondientes y la fecha en que salió (o no).",
            'lw, lwatched': "*(list watched)* Muestra las series ya vistas",
            'lnw, lnwatched': "*(list not watched)* Muestra las series no vistas",
            'lda': "*(list adoptables)* Imprime la base de datos de las series adoptables, aka con 5 tickets.",
            'add, aefu': """
                *(add entry for user)* Agrega una serie a la lista.
                Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
                *Ejemplo: add Tensz Baccano!*
                """,
            'chd': """
                *(change view date)* Cambia la fecha en que se vio una serie. El valor serie y fecha tienen que encontrarse \
                entre comillas dobles o simples, y la fecha en formato DD-MM-YYYY. Si no se indica fecha utiliza la actual.
                *Ejemplo: chd "Nazo No Kanojo X" "23-01-2020"*
                """,
            'remove': """
                Borra una entrada por **nombre** de la base de datos. **CUIDADO:** Acepta resultados parciales por lo que puede borrar entradas indeseadas
                *Ejemplo: remove Boku no Pico*
                """,
            'adopt': """
                Adopta una serie entre las disponibles en *lda*, mantiniendo sus tickets. Es necesario tener un rol con jerarquía correspondiente.
                *Ejemplo: adopt @Bravelycold Ishuzoku Reviewers*
                """,
            'chticks': """
                Cambia la cantidad de tickets de una entrada particular.
                Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
                *Ejemplo: chticks "Boku no Pico" 4*
                """,
            'tick': """
                Suma un ticket a todas las series no vistas en la base de datos. Toma como argumento opcional cuántos tickets se puedn sumar (puede ser un número negativo).
                Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
                """,
            'propuesta': """
                Muestra la propuesta de cierto usuario.
                *Ejemplo: propuesta @jugoprex*
                """
        }
        for k, v in dict_list.items():
            embed.add_field(name=k, value=v, inline=False)
        await ctx.send(embed=embed)
 
    @commands.command(aliases=['on?'])
    async def atiendo_virgos(self, ctx):
        picardia  = self.bot.get_emoji(784272637010509864)
        if picardia:
            await ctx.send("Atiendo virgos. No ves que atiendo virgos? {}".format(picardia))
        else:
            await ctx.send("Atiendo virgos. No ves que atiendo virgos?")

def setup(bot):
    bot.add_cog(Info(bot))