import discord
from discord.ext import commands
import csv
import io

class Extrator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="backup")
    async def backup(self, ctx):
        
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("Você precisa da permissão **Gerenciar Servidor** para fazer isso.")
            return

        guild = ctx.guild
        await ctx.send(f"Iniciando backup de **{guild.name}**... Isso pode levar alguns segundos.")
        print(f"Iniciando extração do servidor: {guild.name}")

        buffer_texto = io.StringIO()
        writer = csv.writer(buffer_texto)
        writer.writerow(['ID', 'User', 'Apelido', 'DataEntrada', 'Bot?'])

        count = 0
        async for member in guild.fetch_members(limit=None):
            join_date = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Desconhecido"
            
            writer.writerow([
                member.id,              
                member.name,            
                member.display_name,    
                join_date,              
                member.bot              
            ])
            count += 1

        print(f"Finalizado! Total: {count} membros.")
        
        buffer_bytes = io.BytesIO(buffer_texto.getvalue().encode('utf-8'))
        
        filename = f"membros_{guild.id}.csv"
        
        await ctx.send(
            f"Arquivo **{filename}** gerado com **{count}** membros.",
            file=discord.File(fp=buffer_bytes, filename=filename)
        )

async def setup(bot):
    await bot.add_cog(Extrator(bot))