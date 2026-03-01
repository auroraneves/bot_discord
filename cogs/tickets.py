import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta, timezone
import io


class Config:
    ADMIN_ROLE_ID = 1462875545015554179 
    CARGO_APROVADO_ID = 1339353453608173638 
    CARGO_REMOVER_ID = 1463174726858834137 
    WELCOME_ID = 1334938033945972802
    LOG_CHANNEL_ID = 1474401518600851528
    FUSO_BR = timezone(timedelta(hours=-3)) # Fuso de Brasília

# Botões Dentro da Thread (Aprovar e Recusar/Fechar)
class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.green, custom_id="aprovar_ticket", emoji="✅")
    async def approve_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_suporte = interaction.guild.get_role(Config.ADMIN_ROLE_ID)
        
        if role_suporte not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Sem permissão para aprovar membros", ephemeral=True)
            return

        if not interaction.message.mentions:
            await interaction.response.send_message("Erro: Não foi encontrado quem abriu o ticket.", ephemeral=True)
            return
            
        membro = interaction.message.mentions[0]
        
        # Checa se a pessoa ainda está no servidor antes de aprovar
        if not isinstance(membro, discord.Member):
            await interaction.response.send_message("Não é possível aprovar. O usuário saiu do servidor.", ephemeral=True)
            return

        cargo_dar = interaction.guild.get_role(Config.CARGO_APROVADO_ID)
        cargo_tirar = interaction.guild.get_role(Config.CARGO_REMOVER_ID)

        # Remove o cargo antigo
        if cargo_tirar and cargo_tirar in membro.roles:
            await membro.remove_roles(cargo_tirar)
        
        # Adiciona o novo cargo
        if cargo_dar:
            await membro.add_roles(cargo_dar)
        
        button.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(f"{membro.mention} foi aprovada! Cargos atualizados com sucesso.", ephemeral=False)

        canal_boas_vindas = interaction.guild.get_channel(Config.WELCOME_ID)
        if canal_boas_vindas:
            mensagem = f"🎉 Boas-vindas à comunidade, {membro.mention}!"
            await canal_boas_vindas.send(mensagem)

    @discord.ui.button(label="Recusar / Fechar", style=discord.ButtonStyle.red, custom_id="fechar_ticket", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_suporte = interaction.guild.get_role(Config.ADMIN_ROLE_ID)
        
        if role_suporte not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Sem permissão para fechar esta verificação.", ephemeral=True)
            return

        await interaction.response.send_message("Fechando ticket e gerando transcrição...", ephemeral=False)
        
        guild = interaction.guild
        canal_ticket = interaction.channel
        usuario_fechou = interaction.user
        
        # Pegar usuário direto da menção
        membro_abriu = interaction.message.mentions[0] if interaction.message.mentions else None
        
        tempo_criacao = canal_ticket.created_at
        tempo_fechamento = discord.utils.utcnow()
        duracao = tempo_fechamento - tempo_criacao
        
        horas, resto = divmod(duracao.total_seconds(), 3600)
        minutos, _ = divmod(resto, 60)
        duracao_str = f"{int(horas)}h {int(minutos)}m"

        # Criando o Transcript (Ajustado para o horário do Brasil)
        texto_log = f"Transcript do Canal: {canal_ticket.name}\n"
        texto_log += f"Data de Fechamento: {tempo_fechamento.astimezone(Config.FUSO_BR).strftime('%d/%m/%Y %H:%M:%S')}\n"
        texto_log += "-" * 50 + "\n\n"
        
        mensagens = [mensagem async for mensagem in canal_ticket.history(limit=None, oldest_first=True)]
        for msg in mensagens:
            data_msg = msg.created_at.astimezone(Config.FUSO_BR).strftime("%d/%m/%Y %H:%M")
            conteudo = msg.content if msg.content else "[Anexo/Embed]"
            texto_log += f"[{data_msg}] {msg.author.name}: {conteudo}\n"
            
        arquivo_txt = discord.File(io.BytesIO(texto_log.encode('utf-8')), filename=f"transcript-{canal_ticket.name}.txt")

        log_channel = guild.get_channel(Config.LOG_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(title="🔒 Ticket Fechado!", color=discord.Color.dark_theme())
            
            nome_usuario = membro_abriu.mention if membro_abriu else "Desconhecido"
            id_usuario = membro_abriu.id if membro_abriu else "Desconhecido"
            avatar_url = membro_abriu.display_avatar.url if membro_abriu else None
            
            embed_log.add_field(name="👤 Usuário", value=f"**Nome:** {nome_usuario}\n**ID:** {id_usuario}", inline=True)
            
            if avatar_url:
                embed_log.set_thumbnail(url=avatar_url)
            
            cargo_aprovado = guild.get_role(Config.CARGO_APROVADO_ID)
        
            # Verifica se ainda é um Member antes de acessar .roles
            status_ticket = "❌ Recusado/Cancelado"
            if membro_abriu and isinstance(membro_abriu, discord.Member):
                if cargo_aprovado and cargo_aprovado in membro_abriu.roles:
                    status_ticket = "✅ Aceito"

            embed_log.add_field(name="Status do Ticket", value=f"`{status_ticket}`", inline=False)
            embed_log.add_field(name="📋 Informações Adicionais", value="**Status:** `closed`", inline=False)
            
            aberto_em = f"<t:{int(tempo_criacao.timestamp())}:F>" 
            fechado_em = f"<t:{int(tempo_fechamento.timestamp())}:F>"
            
            embed_log.add_field(name="⏰ Tempo do Ticket", value=f"**Aberto em:** {aberto_em}\n**Fechado em:** {fechado_em}\n**Duração:** `{duracao_str}`", inline=False)
            embed_log.add_field(name="📛 Fechado por", value=f"{usuario_fechou.mention}\n{usuario_fechou.id}", inline=False)
            
            await log_channel.send(embed=embed_log, file=arquivo_txt)

        await asyncio.sleep(5)
        await canal_ticket.delete()


# Formulario
class VerificationModal(discord.ui.Modal, title='Responda UMA das perguntas abaixo.'):
    rede_social = discord.ui.TextInput(
        label='Mande o link de uma rede social sua ativa',
        style=discord.TextStyle.short,
        placeholder='Envie aqui seu LinkedIn, GitHub, X, etc..',
        required=False 
    )
    
    descricao = discord.ui.TextInput(
        label='Ou descreva sua área de STEM e como nos achou',
        style=discord.TextStyle.paragraph,
        placeholder='Caso prefira não compartilhar redes sociais...',
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
      
        # Impede de enviar se a pessoa não digitou nada em ambas as perguntas
        if not self.rede_social.value.strip() and not self.descricao.value.strip():
            await interaction.response.send_message("⚠️ Você precisa preencher pelo menos um dos campos para continuar!", ephemeral=True)
            return

        await interaction.response.send_message("Formulário enviado com sucesso! Fique atenta pois você será marcada no ticket.", ephemeral=True)
        
        try:
            thread = await interaction.channel.create_thread(
                name=f"verificação-{interaction.user.name}",
                type=discord.ChannelType.private_thread,
                invitable=False
            )
        except Exception:
            thread = await interaction.channel.create_thread(
                name=f"verificação-{interaction.user.name}",
                type=discord.ChannelType.public_thread
            )

        embed = discord.Embed(
            title="Nova Verificação Recebida",
            color=discord.Color.from_rgb(233, 30, 99) 
        )
        embed.add_field(name="Rede Social", value=self.rede_social.value or "Não preenchido", inline=False)
        embed.add_field(name="Área STEM / Como achou", value=self.descricao.value or "Não preenchido", inline=False)

        await thread.send(
            content=f"Olá {interaction.user.mention}, aguarde a análise da <@&{Config.ADMIN_ROLE_ID}>.", 
            embed=embed, 
            view=TicketControls()
        )

# Botão inicial do painel
class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fazer Verificação", style=discord.ButtonStyle.grey, custom_id="verificar_btn", emoji="🔑")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        nome_thread_esperado = f"verificação-{interaction.user.name}"
        
        # Varre todas as threads ativas do servidor para ver se já existe uma igual
        for thread in interaction.guild.threads:
            if thread.name == nome_thread_esperado:
                await interaction.response.send_message(
                    f"Você já possui uma verificação em andamento aqui: {thread.mention}", 
                    ephemeral=True
                )
                return
        
        await interaction.response.send_modal(VerificationModal())

# Painel inicial com msg de boas vindas
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(VerificationView())
        self.bot.add_view(TicketControls())

    @commands.command(name="painel")
    @commands.has_permissions(administrator=True)
    async def painel(self, ctx):
        descricao = (
            "# 🌷 Sobre a Comunidade 💻 \n"
            "Esta é uma comunidade dedicada a mulheres (cis e trans) e pessoas não binárias que atuam ou têm interesse em STEM (Ciência, Tecnologia, Engenharia e Matemática).\n\n"
            "Nosso objetivo é criar um espaço seguro de troca, desenvolvimento, apoio e fortalecimento profissional. Mantemos esse recorte de gênero para promover representatividade, escuta ativa e segurança entre pessoas que historicamente enfrentam barreiras nestes campos.\n\n"
            "**Elegibilidade:**\n\n"
            "Ao solicitar a sua entrada, declara que:\n\n"
            "☐ Se identifica como mulher (cis ou trans) ou pessoa não binária.\n"
            "☐ Está de acordo com o propósito e os valores da comunidade.\n"
            "☐ Compromete-se a respeitar todas as identidades de gênero, orientações, vivências e trajetórias profissionais."
        )

        embed = discord.Embed(
            description=descricao,
            color=discord.Color.from_rgb(233, 30, 99) 
        )
        
        await ctx.send(embed=embed, view=VerificationView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))