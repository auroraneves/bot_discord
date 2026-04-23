import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional
import csv
import io
import re

# Colunas disponíveis e como extraí-las de um Member
COLUNAS_DISPONIVEIS = {
    "id":      lambda m: m.id,
    "user":    lambda m: str(m),
    "apelido": lambda m: m.display_name,
    "entrada": lambda m: m.joined_at.strftime("%Y-%m-%d %H:%M:%S") if m.joined_at else "Desconhecido",
    "bot":     lambda m: m.bot,
    "cargos":  lambda m: ", ".join(r.name for r in m.roles if r.name != "@everyone"),
    "criacao": lambda m: m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
}

COLUNAS_PADRAO = ["id", "user", "apelido", "entrada", "bot"]


def _sanitizar(texto: str) -> str:
    """Remove caracteres inválidos para nome de arquivo."""
    texto = texto.replace(" ", "_")
    return re.sub(r"[^\w\-]", "", texto)  


def _parse_colunas(raw: Optional[str]) -> list:
    """Converte 'id, user, apelido' → ['id', 'user', 'apelido'] validando nomes."""
    if not raw:
        return COLUNAS_PADRAO.copy()

    pedidas = [c.strip().lower() for c in raw.split(",") if c.strip()]
    validas = [c for c in pedidas if c in COLUNAS_DISPONIVEIS]

    return validas if validas else COLUNAS_PADRAO.copy()


class Extrator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
      
    @commands.command(name="backup")
    @commands.has_permissions(manage_guild=True)
    async def backup_prefix(self, ctx: commands.Context):
        """Versão prefixo — usa todas as colunas padrão, sem filtro de cargo."""
        await self._exportar(ctx.send, ctx.guild, cargo=None, colunas=COLUNAS_PADRAO)

    # ──────────────────────────────────────────
    # Slash Command
    # ──────────────────────────────────────────
    @app_commands.command(
        name="backup",
        description="Exporta membros do servidor para CSV."
    )
    @app_commands.describe(
        cargo="(Opcional) Filtra somente membros com esse cargo.",
        colunas=(
            "Colunas separadas por vírgula. "
            "Opções: id, user, apelido, entrada, bot, cargos, criacao. "
            "Padrão: todas."
        ),
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def backup_slash(
        self,
        interaction: discord.Interaction,
        cargo: Optional[discord.Role] = None,
        colunas: Optional[str] = None,
    ):
        await interaction.response.defer(thinking=True)

        colunas_lista = _parse_colunas(colunas)

        async def send_fn(**kwargs):
            await interaction.followup.send(**kwargs)

        await self._exportar(send_fn, interaction.guild, cargo, colunas_lista)

    # ──────────────────────────────────────────
    # Exportação
    # ──────────────────────────────────────────
    async def _exportar(self, send_fn, guild: discord.Guild, cargo, colunas: list):
        descricao_cargo = f" com cargo **{cargo.name}**" if cargo else ""
        await send_fn(
            content=f"⏳ Gerando CSV de **{guild.name}**{descricao_cargo}..."
        )

        buffer_texto = io.StringIO()
        writer = csv.writer(buffer_texto)
        writer.writerow([c.upper() for c in colunas])

        count = 0
        async for member in guild.fetch_members(limit=None):
            if cargo and cargo not in member.roles:
                continue

            writer.writerow([COLUNAS_DISPONIVEIS[c](member) for c in colunas])
            count += 1

        # Nome de arquivo legível
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        nome_servidor = _sanitizar(guild.name)
        sufixo_cargo = f"_{_sanitizar(cargo.name)}" if cargo else ""
        filename = f"membros_{nome_servidor}{sufixo_cargo}_{data_hoje}.csv"

        buffer_bytes = io.BytesIO(buffer_texto.getvalue().encode("utf-8"))

        await send_fn(
            content=f"**{filename}** gerado com **{count}** membros.",
            file=discord.File(fp=buffer_bytes, filename=filename),
        )

    # ──────────────────────────────────────────
    # Tratamento de erros do slash command
    # ──────────────────────────────────────────
    @backup_slash.error
    async def backup_slash_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Você precisa da permissão **Gerenciar Servidor** para isso.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"Erro inesperado: `{error}`", ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Extrator(bot))