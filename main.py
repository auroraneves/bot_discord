import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

class AuroraBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        print("Carregando módulos...")
        await self.load_extension('cogs.exportar_membros')
        print("Módulo 'exportar_membros' carregado!")
        
        await self.load_extension('cogs.tickets')
        print("Módulo 'tickets' carregado!")
        
        await self.load_extension('cogs.verificar_presenca')
        print("Módulo 'verificar_presenca' carregado!")
        
        print("Sincronizando comandos com o Discord...")
        await self.tree.sync()

    async def on_ready(self):
        print('--------------------------------------------------')
        print(f'Bot conectado com sucesso como: {self.user}')
        print('--------------------------------------------------')

if __name__ == '__main__':
    AuroraBot().run(TOKEN)
