from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os
import sys

# ==================== KEEP-ALIVE SERVER ====================
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot Discord está online! Acesse /health para status."

@app.route('/health')
def health():
    return "🟢 ONLINE", 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Servidor keep-alive iniciado na porta 8080")

# ==================== BOT DISCORD ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # IMPORTANTE para tickets/sets

bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== CARREGAR MÓDULOS ====================
print("📦 Carregando módulos...")

try:
    # Carregar módulo de events
    from modules import events
    print("✅ Módulo 'events' carregado")
except ImportError as e:
    print(f"❌ Erro ao carregar 'events': {e}")

try:
    # Carregar módulo de commands
    from modules import commands
    print("✅ Módulo 'commands' carregado")
except ImportError as e:
    print(f"❌ Erro ao carregar 'commands': {e}")

# Carregar COGs (tickets, sets, etc.)
async def load_cogs():
    print("🔄 Carregando COGs...")
    
    # Lista de COGs para carregar
    cogs = [
        'modules.tickets',      # Se tiver arquivo tickets.py
        'modules.sets',         # Se tiver arquivo sets.py
        'modules.events',       # Events como COG
        'modules.commands'      # Commands como COG
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ COG '{cog}' carregado")
        except commands.ExtensionNotFound:
            print(f"⚠️  COG '{cog}' não encontrado")
        except Exception as e:
            print(f"❌ Erro ao carregar '{cog}': {e}")

# ==================== EVENTOS ====================
@bot.event
async def on_ready():
    print(f'✅ Bot logado como: {bot.user}')
    print(f'🆔 ID: {bot.user.id}')
    print(f'📡 Ping: {round(bot.latency * 1000)}ms')
    print('🚀 Bot pronto para uso!')
    
    # Sincronizar comandos slash (se usar)
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos slash sincronizados")
    except Exception as e:
        print(f"⚠️  Erro ao sincronizar comandos: {e}")

# ==================== COMANDOS BÁSICOS ====================
@bot.command()
async def ping(ctx):
    """Responde com a latência do bot"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! {latency}ms')

@bot.command()
async def reload(ctx):
    """Recarrega todos os módulos (apenas dono)"""
    if ctx.author.id != YOUR_DISCORD_ID:  # Substitua pelo seu ID
        return await ctx.send("❌ Apenas o dono pode usar este comando!")
    
    await load_cogs()
    await ctx.send("✅ Módulos recarregados!")

# ==================== INICIALIZAÇÃO ====================
if __name__ == '__main__':
    print("🚀 Iniciando bot Discord...")
    
    # Verificar token
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        sys.exit(1)
    
    print("✅ Token encontrado")
    
    # Iniciar keep-alive
    keep_alive()
    
    # Carregar COGs antes de iniciar
    import asyncio
    asyncio.run(load_cogs())
    
    # Iniciar bot
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido ou expirado!")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
