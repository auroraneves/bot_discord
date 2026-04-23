# AuroraBot

AuroraBot é um bot de gestão do servidor STEM Girls, desenvolvido em Python com a biblioteca `discord.py`. Suas funcionalidades são organizadas em Cogs, módulos independentes que facilitam a manutenção e expansão do projeto. Por enquanto, o bot está disponível apenas no servidor do STEM Girls.

## Como usar

O bot possui três comandos voltados para a moderação do servidor.

**`!painel`** — Cria o painel de entrada do servidor.

**`!backup`** — Exporta a lista completa de membros do servidor em um arquivo `.csv`, contendo ID, nome de usuário, apelido, data de entrada e uma flag indicando se a conta é um bot.

**`/checar_lista`** — Cruza um arquivo `.csv` externo, como uma lista gerada por formulário de inscrição, com os membros ativos do servidor. Aceita como parâmetros o arquivo CSV, o índice da coluna com os identificadores e uma flag booleana para definir se a busca será feita por IDs numéricos ou por nomes de usuário. O resultado é enviado como embed com um resumo da verificação e um arquivo `.txt` listando os ausentes.

Todos os comandos são restritos a membros com a permissão de Gerenciar Servidor.

## Estrutura do Projeto

```
auroraneves-bot_discord/
├── discloud.config
├── main.py
└── cogs/
    ├── exportar_membros.py
    ├── tickets.py
    └── verificar_presenca.py
```

O arquivo `main.py` é o ponto de entrada do bot. A classe `AuroraBot` estende `commands.Bot`, carrega os três Cogs no `setup_hook` e sincroniza os comandos de barra com a API do Discord. As Intents habilitadas são `members` e `message_content`, ambas necessárias para o funcionamento correto dos comandos.
