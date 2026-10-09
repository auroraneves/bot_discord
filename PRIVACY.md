# Política de Privacidade / Privacy Policy — AuroraBot (Lola)

**Última atualização / Last updated:** 09/10/2026

🇧🇷 [Português](#português) · 🇬🇧 [English](#english)

---

## Português

### 1. Sobre o bot
O AuroraBot (exibido no Discord como **Lola**) é um bot de gestão e moderação desenvolvido para a comunidade **STEM Girls**. Ele funciona apenas nesse servidor e é operado pela equipe de moderação responsável por ele.

### 2. Quais dados são acessados e por quê

| Dado | Finalidade |
|---|---|
| ID, nome de usuário, apelido, cargos e data de entrada dos membros (*Server Members Intent*) | Verificar membros novos, trocar cargos após a aprovação, identificar quem não iniciou a verificação em 48 horas, exportar a lista de membros (`/backup`) e cruzar listas externas com os membros do servidor (`/checar_lista`) |
| Texto, anexos e embeds das mensagens dentro dos tickets de verificação (*Message Content Intent*) | Gerar a transcrição do ticket para a equipe de moderação quando ele é encerrado |
| Comandos com prefixo (`!painel`, `!backup`) (*Message Content Intent*) | Permitir que a equipe use esses comandos |
| IDs de membros que já receberam aviso de verificação pendente | Evitar avisos duplicados |

O bot **não** utiliza a Presence Intent e **não** acessa o status online, atividades ou jogos dos usuários.
O bot **não** lê nem registra mensagens fora dos tickets de verificação, exceto o necessário para identificar os comandos acima.

### 3. Como os dados são usados e compartilhados
- Os dados são usados **somente** para as finalidades listadas acima, dentro do servidor STEM Girls.
- **Não vendemos, alugamos nem compartilhamos** dados com terceiros, e não os usamos para publicidade, análise de perfil ou treinamento de modelos de IA.
- Exportações (`/backup`, `/checar_lista`) e transcrições de tickets são enviadas apenas à pessoa que executou o comando ou ao canal de logs da moderação, restritos a pessoas autorizadas.

### 4. Armazenamento e retenção
- Exportações e transcrições são geradas em memória e enviadas ao Discord; **o bot não as guarda em disco**. Depois de enviadas, ficam no Discord (canal de logs ou mensagem do comando) e seguem as regras da plataforma e a gestão da moderação.
- O bot mantém apenas um arquivo local com **IDs numéricos** de membros que já foram avisados, sem nomes nem mensagens. Esse registro é mantido enquanto for necessário para a verificação.
- O token e as configurações do bot ficam em ambiente privado de hospedagem e não são divulgados.

### 5. Seus direitos
Você pode pedir informações sobre os dados do bot relacionados a você, a correção deles ou a exclusão dos registros mantidos pela moderação (como a transcrição do seu ticket e seu ID no arquivo de avisos). Entre em contato pelo canal abaixo. Dados que estão no Discord também são regidos pela [Política de Privacidade do Discord](https://discord.com/privacy).

### 6. Segurança
Os comandos administrativos são restritos a quem tem as permissões de *Gerenciar Servidor* ou *Administrador*. O acesso ao ambiente de hospedagem é restrito à pessoa responsável pelo bot.

### 7. Alterações
Esta política pode ser atualizada. A data no topo indica a versão mais recente.

### 8. Contato
Para dúvidas ou solicitações: **[SEU E-MAIL OU USUÁRIO DO DISCORD AQUI]**

---

## English

### 1. About the bot
AuroraBot (shown on Discord as **Lola**) is a management and moderation bot built for the **STEM Girls** community. It runs only on that server and is operated by the moderation team responsible for it.

### 2. What data is accessed and why

| Data | Purpose |
|---|---|
| Member ID, username, nickname, roles and join date (*Server Members Intent*) | Verify new members, swap roles upon approval, identify members who haven't started verification within 48 hours, export the member list (`/backup`) and cross-reference external lists with server members (`/checar_lista`) |
| Text, attachments and embeds of messages inside verification tickets (*Message Content Intent*) | Generate a ticket transcript for the moderation team when a ticket is closed |
| Prefix commands (`!painel`, `!backup`) (*Message Content Intent*) | Allow staff to use these commands |
| IDs of members who have already been warned about pending verification | Avoid duplicate warnings |

The bot does **not** use the Presence Intent and does **not** access users' online status, activities or games.
The bot does **not** read or record messages outside verification tickets, other than what is needed to detect the commands above.

### 3. How data is used and shared
- Data is used **only** for the purposes listed above, inside the STEM Girls server.
- We **do not sell, rent or share** data with third parties, and we do not use it for advertising, profiling or AI model training.
- Exports (`/backup`, `/checar_lista`) and ticket transcripts are delivered only to the person who ran the command or to the moderation log channel, which is restricted to authorized staff.

### 4. Storage and retention
- Exports and transcripts are generated in memory and sent to Discord; **the bot does not store them on disk**. Once sent, they live on Discord (log channel or command reply) and are subject to the platform's rules and the moderation team's management.
- The bot keeps only a local file with **numeric IDs** of members who have already been warned, with no names or messages. This record is kept for as long as it is needed for the verification process.
- The bot token and configuration are kept in a private hosting environment and are never disclosed.

### 5. Your rights
You may request information about the bot-related data we hold about you, its correction, or the deletion of records kept by the moderation team (such as your ticket transcript and your ID in the warnings file). Contact us using the details below. Data stored on Discord is also governed by [Discord's Privacy Policy](https://discord.com/privacy).

### 6. Security
Administrative commands are restricted to users with the *Manage Server* or *Administrator* permission. Access to the hosting environment is restricted to the person responsible for the bot.

### 7. Changes
This policy may be updated. The date at the top shows the latest version.

### 8. Contact
For questions or requests: **[YOUR EMAIL OR DISCORD USERNAME HERE]**
