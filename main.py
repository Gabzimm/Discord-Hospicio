from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os
import sys
import asyncio

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

# ==================== CARREGAR SEUS MÓDULOS ====================
async def load_cogs():
    """Carrega seus módulos (tickets, sets, etc.)"""
    print("🔄 Carregando seus módulos...")
    
    # Lista dos SEUS módulos
    cogs = [
        'modules.tickets',  # ← SEU SISTEMA DE TICKETS
        'modules.sets',     # ← SEU SISTEMA DE SETS
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Módulo '{cog}' carregado com sucesso!")
        except commands.ExtensionNotFound:
            print(f"⚠️  Módulo '{cog}' não encontrado")
        except commands.ExtensionFailed as e:
            print(f"❌ Erro ao carregar '{cog}': {e}")
        except Exception as e:
            print(f"❌ Erro inesperado em '{cog}': {e}")

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
        print(f"⚠️  Não foi possível sincronizar comandos slash: {e}")

# ==================== COMANDOS BÁSICOS ====================
@bot.command()
async def ping(ctx):
    """Responde com a latência do bot"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! {latency}ms')

@bot.command()
async def reload(ctx):
    """Recarrega todos os módulos (apenas dono)"""
    # Substitua 123456789012345678 pelo SEU ID do Discord
    if ctx.author.id != 1213819385576300595:  
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
        print("💡 Configure em: Render Dashboard → Environment → Add Variable")
        sys.exit(1)
    
    print("✅ Token encontrado")
    
    # Iniciar keep-alive
    keep_alive()
    
    # Carregar SEUS módulos antes de iniciar
    async def startup():
        await load_cogs()
    
    # Executar carregamento
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(startup())
    
    # Iniciar bot
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido ou expirado!")
        print("💡 Gere um novo token em: https://discord.com/developers/applications")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
