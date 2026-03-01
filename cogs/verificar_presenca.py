import discord
from discord.ext import commands
from discord import app_commands
import csv
import io

class VerificarPresenca(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="checar_lista", description="Cruza um arquivo CSV com os membros atuais do servidor.")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(
        arquivo="O arquivo CSV com a lista gerada pelo formulário.",
        coluna_dados="Índice da coluna com os nomes/IDs.",
        comparar_por_id="Selecione True SE a planilha usar IDs numéricos. O default é buscar por @'s'"
    )
    async def checar_lista(self, interaction: discord.Interaction, arquivo: discord.Attachment, coluna_dados: int, comparar_por_id: bool = False):
        
        if not arquivo.filename.endswith('.csv'):
            await interaction.response.send_message("⚠️ O arquivo precisa ser um `.csv`.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)

        csv_bytes = await arquivo.read()
        
        try:
            csv_texto = csv_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            csv_texto = csv_bytes.decode('cp1252')
        
        leitor_csv = csv.reader(io.StringIO(csv_texto))
        linhas = list(leitor_csv)

        if len(linhas) <= 1:
            await interaction.followup.send("O arquivo parece estar vazio ou não tem cabeçalho.")
            return

        presentes = []
        ausentes = []
        guild = interaction.guild
        
        for linha in linhas[1:]:
            if not linha or len(linha) <= coluna_dados: 
                continue
            
            texto_limpo = linha[coluna_dados].strip()
            
            if not texto_limpo: 
                continue
            
            alvo_identificado = texto_limpo
            membro = None
            
            if comparar_por_id:
                if texto_limpo.isdigit():
                    membro = guild.get_member(int(texto_limpo))
            else:
                nome_limpo = texto_limpo.lstrip('@').lower() 
                membro = discord.utils.get(guild.members, name=nome_limpo)
            
            if membro:
              # INNER JOIN
                presentes.append(f"{membro.display_name} ({alvo_identificado})")
            else:
              # LEFT ANTI JOIN
                ausentes.append(alvo_identificado)

        tipo_busca = "IDs Numéricos" if comparar_por_id else "Nomes de Usuário"
        relatorio_texto = f"--- RELATÓRIO DE PRESENÇA ({tipo_busca}) ---\n"
        relatorio_texto += f"Índice da coluna analisada: {coluna_dados}\n"
        relatorio_texto += f"Total de dados válidos lidos: {len(presentes) + len(ausentes)}\n"
        relatorio_texto += f"Presentes no servidor: {len(presentes)}\n"
        relatorio_texto += f"Ausentes no servidor: {len(ausentes)}\n\n"
        
        relatorio_texto += "--- MEMBROS AUSENTES ---\n"
        if ausentes:
            for ausente in ausentes:
                relatorio_texto += f"{ausente}\n"
        else:
            relatorio_texto += "Todos da lista estão no servidor!\n"

        buffer_bytes = io.BytesIO(relatorio_texto.encode('utf-8'))
        arquivo_relatorio = discord.File(fp=buffer_bytes, filename="ausentes.txt")

        embed = discord.Embed(
            title="Verificação Concluída", 
            description=f"Cruzamento de dados finalizado buscando no **índice {coluna_dados}**.",
            color=discord.Color.from_rgb(233, 30, 99)
        )
        embed.add_field(name="✅ Encontrados", value=f"{len(presentes)} pessoas", inline=True)
        embed.add_field(name="❌ Não Encontrados", value=f"{len(ausentes)} pessoas", inline=True)
        
        await interaction.followup.send(embed=embed, file=arquivo_relatorio)

async def setup(bot):
    await bot.add_cog(VerificarPresenca(bot))