import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta, timezone
import io
import json
import os


class Config:
    ADMIN_ROLE_ID = 1462875545015554179 
    CARGO_APROVADO_ID = 1339353453608173638 
    CARGO_REMOVER_ID = 1463174726858834137 
    WELCOME_ID = 1334938033945972802
    LOG_CHANNEL_ID = 1474401518600851528
    PAINEL_CHANNEL_ID = 1462867539410423829
    FUSO_BR = timezone(timedelta(hours=-3)) # Fuso de Brasília
    AVISADOS_FILE = "membros_avisados.json" # Arquivo para persistir quem já foi avisado


def _carregar_avisados() -> set:
    if os.path.exists(Config.AVISADOS_FILE):
        try:
            with open(Config.AVISADOS_FILE, "r") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            pass
    return set()


def _salvar_avisados(avisados: set):
    try:
        with open(Config.AVISADOS_FILE, "w") as f:
            json.dump(list(avisados), f)
    except IOError:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Botões Dentro da Thread (Aprovar e Recusar/Fechar)
# ─────────────────────────────────────────────────────────────────────────────
class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.green, custom_id="aprovar_ticket", emoji="✅")
    async def approve_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_suporte = interaction.guild.get_role(Config.ADMIN_ROLE_ID)
        
        if role_suporte not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Você não tem permissão para aprovar membros", ephemeral=True)
            return

        if not interaction.message.mentions:
            await interaction.response.send_message("Erro: Não foi encontrado quem abriu o ticket.", ephemeral=True)
            return
            
        membro = interaction.message.mentions[0]
        
        # Checa se a pessoa ainda está no servidor antes de aprovar
        if not isinstance(membro, discord.Member):
            await interaction.response.send_message("Não é possível aprovar pois a pessoa saiu do servidor.", ephemeral=True)
            return

        # Defer imediatamente para evitar timeout de 3s do Discord
        await interaction.response.defer()

        cargo_dar = interaction.guild.get_role(Config.CARGO_APROVADO_ID)
        cargo_tirar = interaction.guild.get_role(Config.CARGO_REMOVER_ID)

        # Remove o cargo antigo
        if cargo_tirar and cargo_tirar in membro.roles:
            await membro.remove_roles(cargo_tirar)
        
        # Adiciona o novo cargo
        if cargo_dar:
            await membro.add_roles(cargo_dar)

        # Limpa o ID do set ao aprovar
        avisados = _carregar_avisados()
        if membro.id in avisados:
            avisados.discard(membro.id)
            _salvar_avisados(avisados)
        
        button.disabled = True
        try:
            await interaction.message.edit(view=self)
        except discord.NotFound:
            pass  # Mensagem já foi deletada, ignora

        await interaction.followup.send(f"{membro.mention} foi aprovada! Cargos atualizados com sucesso.")

        canal_boas_vindas = interaction.guild.get_channel(Config.WELCOME_ID)
        if canal_boas_vindas:
            mensagem = f"🎉 Boas-vindas {membro.mention}! Pegue seus cargos em <#1426721213186703370>."
            await canal_boas_vindas.send(mensagem)

    @discord.ui.button(label="Recusar / Fechar", style=discord.ButtonStyle.red, custom_id="fechar_ticket", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_suporte = interaction.guild.get_role(Config.ADMIN_ROLE_ID)
        
        if role_suporte not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Sem permissão para fechar esta verificação.", ephemeral=True)
            return

        # Defer imediatamente para evitar timeout de 3s do Discord
        await interaction.response.defer()
        await interaction.followup.send("Fechando ticket, checando status do usuário e gerando transcrição...")
        
        guild = interaction.guild
        canal_ticket = interaction.channel
        usuario_fechou = interaction.user
        
        # Pegar usuário direto da menção
        membro_abriu = interaction.message.mentions[0] if interaction.message.mentions else None
        
        # --- LÓGICA DE EXPULSÃO (KICK) ---
        cargo_aprovado = guild.get_role(Config.CARGO_APROVADO_ID)
        status_ticket = "❌ Saiu do Server"
        
        if membro_abriu and isinstance(membro_abriu, discord.Member):
            if cargo_aprovado and cargo_aprovado in membro_abriu.roles:
                status_ticket = "✅ Aceita"
            else:
                status_ticket = "❌ Recusada"

                # Limpa do set de avisados já que vai ser expulsa
                avisados = _carregar_avisados()
                if membro_abriu.id in avisados:
                    avisados.discard(membro_abriu.id)
                    _salvar_avisados(avisados)

                try:
                    await membro_abriu.send(
                        "Oi.. Sua solicitação de entrada no STEM Girls foi recusada pela equipe :( \n"
                        "Nossa comunidade é voltada para mulheres (cis ou trans) e pessoas não-binárias na área de STEM. \n"
                        "Se você acredita que houve um engano, entre novamente no servidor e abra um novo ticket explicando melhor a sua situação. 🌷"
                    )
                except discord.Forbidden:
                    pass # Ignora se a DM da pessoa estiver trancada
                
                try:
                    await membro_abriu.kick(reason=f"Verificação recusada por {usuario_fechou.name}.")
                except discord.Forbidden:
                    status_ticket = "❌ Recusada (Erro: Bot sem permissão para expulsar)"

        # --- GERAÇÃO DA TRANSCRIÇÃO ---
        tempo_criacao = canal_ticket.created_at
        tempo_fechamento = discord.utils.utcnow()
        duracao = tempo_fechamento - tempo_criacao
        
        horas, resto = divmod(duracao.total_seconds(), 3600)
        minutos, _ = divmod(resto, 60)
        duracao_str = f"{int(horas)}h {int(minutos)}m"

        texto_log = f"--- TRANSCRIPT DO TICKET ---\n"
        texto_log += f"Canal: {canal_ticket.name}\n"
        texto_log += f"Data de Fechamento: {tempo_fechamento.astimezone(Config.FUSO_BR).strftime('%d/%m/%Y %H:%M:%S')}\n"
        texto_log += "-" * 50 + "\n\n"
        
        try:
            mensagens = [mensagem async for mensagem in canal_ticket.history(limit=None, oldest_first=True)]
        except discord.NotFound:
            return  # Canal já foi deletado antes de gerar a transcrição
        
        for i, msg in enumerate(mensagens):
            data_msg = msg.created_at.astimezone(Config.FUSO_BR).strftime("%d/%m/%Y %H:%M")
            partes = []
            
            if msg.content:
                partes.append(msg.content)
            
            if msg.embeds:
                for embed in msg.embeds:
                    if embed.title:
                        partes.append(f"\n[Embed: {embed.title}]")
                    if embed.description:
                        partes.append(embed.description)
                    for field in embed.fields:
                        partes.append(f"\n> {field.name}:\n> {field.value}")
                        
            if msg.attachments:
                for anexo in msg.attachments:
                    partes.append(f"\n[Arquivo Anexado: {anexo.url}]")
                    
            conteudo_final = "".join(partes) if partes else "[Mensagem de Sistema]"
            
            texto_log += f"[{data_msg}] {msg.author.name}:\n{conteudo_final}\n"
            
            if i == 0:
                texto_log += "-" * 30 + "\n"
            else:
                texto_log += "\n"
                
        texto_log += "-" * 30 + "\n"
        arquivo_txt = discord.File(io.BytesIO(texto_log.encode('utf-8')), filename=f"transcript-{canal_ticket.name}.txt")

        # --- ENVIO DO LOG ---
        log_channel = guild.get_channel(Config.LOG_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(title="🔒 Ticket Fechado!", color=discord.Color.dark_theme())
            
            nome_usuario = membro_abriu.mention if membro_abriu else "Desconhecido"
            id_usuario = membro_abriu.id if membro_abriu else "Desconhecido"
            avatar_url = membro_abriu.display_avatar.url if (membro_abriu and hasattr(membro_abriu, 'display_avatar')) else None
            
            embed_log.add_field(name="👤 Usuário", value=f"**Nome:** {nome_usuario}\n**ID:** {id_usuario}", inline=True)
            if avatar_url:
                embed_log.set_thumbnail(url=avatar_url)

            embed_log.add_field(name="Status do Ticket", value=f"`{status_ticket}`", inline=False)
            
            aberto_em = f"<t:{int(tempo_criacao.timestamp())}:F>" 
            fechado_em = f"<t:{int(tempo_fechamento.timestamp())}:F>"
            
            embed_log.add_field(name="⏰ Tempo do Ticket", value=f"**Aberto em:** {aberto_em}\n**Fechado em:** {fechado_em}\n**Duração:** `{duracao_str}`", inline=False)
            embed_log.add_field(name="📛 Fechado por", value=f"{usuario_fechou.mention}\n{usuario_fechou.id}", inline=False)
            
            await log_channel.send(embed=embed_log, file=arquivo_txt)

        await asyncio.sleep(5)
        try:
            await canal_ticket.delete()
        except discord.NotFound:
            pass  # Canal já foi deletado, ignora


# ─────────────────────────────────────────────────────────────────────────────
# Formulário
# ─────────────────────────────────────────────────────────────────────────────
class VerificationModal(discord.ui.Modal, title='Responda UMA das perguntas abaixo.'):
    rede_social = discord.ui.TextInput(
        label='Mande o link de uma rede social sua ativa',
        style=discord.TextStyle.short,
        placeholder='Envie aqui o link de seu LinkedIn, GitHub, X e etc',
        required=False 
    )
    
    descricao = discord.ui.TextInput(
        label='Ou descreva sua área de STEM e como nos achou',
        style=discord.TextStyle.paragraph,
        placeholder='Não quer compartilhar suas redes? Responda aqui com detalhes.',
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
      
        # Impede de enviar se a pessoa não digitou nada em ambas as perguntas
        if not self.rede_social.value.strip() and not self.descricao.value.strip():
            await interaction.response.send_message("⚠️ Você precisa preencher pelo menos um dos campos para continuar!", ephemeral=True)
            return

        # Responde imediatamente para não estourar o timeout de 3s do Discord
        try:
            await interaction.response.send_message("Formulário enviado com sucesso! Fique atenta pois você será marcada no ticket.", ephemeral=True)
        except discord.NotFound:
            return  # Interação expirou antes de responder, ignora

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


# ─────────────────────────────────────────────────────────────────────────────
# Botão inicial do painel
# ─────────────────────────────────────────────────────────────────────────────
class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fazer Verificação", style=discord.ButtonStyle.green, custom_id="verificar_btn", emoji="🔑")
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
        
        # Tenta abrir o modal — ignora se a interação já expirou (3s do Discord)
        try:
            await interaction.response.send_modal(VerificationModal())
        except discord.NotFound:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Cog principal
# ─────────────────────────────────────────────────────────────────────────────
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.membros_avisados = _carregar_avisados()
        self.monitorar_inatividade.start()

    def cog_unload(self):
        self.monitorar_inatividade.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(VerificationView())
        self.bot.add_view(TicketControls())

    @commands.command(name="painel")
    @commands.has_permissions(administrator=True)
    async def painel(self, ctx):
        descricao = (
            "# 🌷 Elegibilidade 💻 \n"
            "Ao solicitar a sua entrada, declara que:\n\n"
            "☐ Se identifica como mulher (cis ou trans) ou pessoa não binária.\n"
            "☐ Está de acordo com o propósito e os valores da comunidade.\n"
            "☐ Compromete-se a respeitar todas as identidades de gênero, orientações, vivências e trajetórias profissionais."
        )

        embed = discord.Embed(
            description=descricao,
            color=discord.Color.from_rgb(233, 30, 99) 
        )
        embed.set_image(url="https://imgur.com/a2QJooO.png")
        await ctx.send(embed=embed, view=VerificationView())

    # ── Loop de monitoramento (roda a cada 1 hora) ────────────────────────────
    @tasks.loop(hours=1)
    async def monitorar_inatividade(self):
        canal_painel = self.bot.get_channel(Config.PAINEL_CHANNEL_ID)
        if not canal_painel:
            return

        guild = canal_painel.guild
        cargo_aprovado = guild.get_role(Config.CARGO_APROVADO_ID)
        cargo_nao_verificado = guild.get_role(Config.CARGO_REMOVER_ID)
        agora = discord.utils.utcnow()

        for membro in guild.members:
            await asyncio.sleep(0.5)

            if membro.bot:
                continue

            # Ignora quem não tem o cargo de não verificado (ex: admins sem cargo de membro)
            if cargo_nao_verificado and cargo_nao_verificado not in membro.roles:
                continue

            if cargo_aprovado in membro.roles:
                continue

            nome_thread_esperado = f"verificação-{membro.name}"
            tem_ticket = any(thread.name == nome_thread_esperado for thread in guild.threads)

            if tem_ticket:
                continue

            if not membro.joined_at:
                continue

            tempo_no_servidor = agora - membro.joined_at
            horas_no_servidor = tempo_no_servidor.total_seconds() / 3600

            # Passou de 48 horas → kick
            if horas_no_servidor >= 48:
                try:
                    await membro.send(
                        "Você foi removida do servidor STEM Girls pois não iniciou o processo "
                        "de verificação no prazo de 48 horas. Você pode tentar entrar novamente "
                        "quando tiver disponibilidade.\n"
                        "https://discord.gg/stemgirls"
                    )
                except discord.Forbidden:
                    pass

                try:
                    await membro.kick(reason="Inatividade: Não abriu ticket de verificação em 48h.")
                except discord.Forbidden:
                    pass

                self.membros_avisados.discard(membro.id)
                _salvar_avisados(self.membros_avisados)
                continue

            elif horas_no_servidor >= 24 and membro.id not in self.membros_avisados:
                try:
                    await canal_painel.send(
                        content=(
                            f"{membro.mention} Faça sua verificação clicando no BOTÃO VERDE, "
                            f"ou você será removida do servidor em breve!!"
                        ),
                        delete_after=20
                    )
                except discord.Forbidden:
                    pass

                self.membros_avisados.add(membro.id)
                _salvar_avisados(self.membros_avisados)

    @monitorar_inatividade.before_loop
    async def before_monitorar(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Tickets(bot))
