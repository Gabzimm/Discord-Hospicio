from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os
import sys
import asyncio
from datetime import datetime

print("=" * 50)
print("🤖 BOT DE CARGO AUTOMÁTICO 24/7")
print("=" * 50)

# ==================== CORREÇÃO DO FLASK ====================
# CORREÇÃO: NÃO usar Flask('') - usar Flask(__name__) e configurar corretamente
app = Flask(__name__)

# CORREÇÃO: Desabilitar debug no Render
app.config['DEBUG'] = False

# CORREÇÃO: Suprimir logs do Flask que causam erro
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Bot de Cargo Automático</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(0,0,0,0.7);
                padding: 30px;
                border-radius: 15px;
                max-width: 600px;
                margin: 0 auto;
            }
            .status {
                background: #28a745;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                font-size: 24px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bot de Cargo Automático</h1>
            <div class="status">🟢 ONLINE 24/7</div>
            <p>Atribui cargo <strong>𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲</strong> automaticamente</p>
            <p>Monitorado por UptimeRobot</p>
            <p><small>{} - {}</small></p>
        </div>
    </body>
    </html>
    """.format(datetime.now().strftime('%d/%m/%Y'), datetime.now().strftime('%H:%M:%S'))

@app.route('/health')
def health():
    return "🟢 ONLINE", 200

@app.route('/ping')
def ping():
    return "pong", 200

# CORREÇÃO: Função run_flask modificada
def run_flask():
    try:
        print("🌐 Tentando iniciar Flask na porta 8080...")
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
    except ImportError:
        # Se waitress não estiver instalado, usar o servidor de desenvolvimento
        print("⚠️ Waitress não instalado, usando servidor de desenvolvimento")
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

def start_web_server():
    print("🌐 Iniciando servidor web na porta 8080...")
    t = Thread(target=run_flask, daemon=True)
    t.start()
    # Dar tempo para o Flask iniciar
    import time
    time.sleep(2)
    print("✅ Servidor web iniciado!")
    print("📡 URLs para UptimeRobot:")
    print("   • /health - Para health check")
    print("   • /ping - Para ping simples")

# ==================== CONFIGURAÇÃO DO BOT ====================

# Configurar intents (APENAS O NECESSÁRIO)
intents = discord.Intents.default()
intents.members = True  # IMPORTANTE: Para detectar quando membros entram

# Criar bot (SIMPLES)
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None  # Sem ajuda, bot minimalista
)

# ==================== EVENTO PRINCIPAL ====================

@bot.event
async def on_member_join(member):
    """ATRIBUI CARGO AUTOMATICAMENTE QUANDO ALGUÉM ENTRA"""
    print(f"\n{'='*50}")
    print(f"👤 NOVO MEMBRO: {member.name}")
    print(f"🏠 Servidor: {member.guild.name}")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # 1. Buscar cargo "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲" (COM ESTA FONTE ESPECÍFICA)
        cargo_nome = "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲"
        cargo = discord.utils.get(member.guild.roles, name=cargo_nome)
        
        # 2. Se não existir, criar
        if not cargo:
            print(f"⚠️ Cargo '{cargo_nome}' não encontrado. Criando...")
            
            try:
                cargo = await member.guild.create_role(
                    name=cargo_nome,
                    color=discord.Color.light_grey(),
                    reason="Criado automaticamente pelo bot"
                )
                print(f"✅ Cargo criado!")
            except:
                print("❌ Não tenho permissão para criar cargos!")
                print("💡 Dê ao bot permissão 'Gerenciar Cargos'")
                return
        
        # 3. Verificar se bot pode gerenciar cargos
        bot_member = member.guild.me
        if not bot_member.guild_permissions.manage_roles:
            print("❌ Não tenho permissão para gerenciar cargos!")
            return
        
        # 4. Atribuir cargo
        await member.add_roles(cargo)
        print(f"✅ Cargo atribuído a {member.name}")
        print(f"📊 Total de membros: {member.guild.member_count}")
        
        # 5. Opcional: Enviar mensagem
        try:
            # Buscar canal de entrada
            for channel in member.guild.text_channels:
                if "entrada" in channel.name.lower() or "geral" in channel.name.lower():
                    if channel.permissions_for(bot_member).send_messages:
                        await channel.send(f"👋 Bem-vindo(a), {member.mention}! Recebeu cargo {cargo.mention}")
                        break
        except:
            pass  # Ignorar erro se não conseguir enviar
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print(f"{'='*50}")

# ==================== EVENTO QUANDO BOT ESTÁ PRONTO ====================

@bot.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"✅ BOT CONECTADO: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print(f"🏠 Servidores: {len(bot.guilds)}")
    
    if bot.guilds:
        print("📋 Servidores conectados:")
        for guild in bot.guilds:
            print(f"   • {guild.name} ({guild.member_count} membros)")
    else:
        print("⚠️ Adicione o bot a um servidor!")
    
    # Status simples
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="👥 novos membros"
        )
    )
    
    print("🎯 Pronto para atribuir cargos automaticamente!")
    print(f"{'='*50}")

# ==================== COMANDO SIMPLES DE TESTE ====================

@bot.command()
async def ping(ctx):
    """Testa se o bot está online"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latency}ms | Online 24/7")

@bot.command()
async def status(ctx):
    """Status do bot"""
    embed = discord.Embed(
        title="🤖 Status do Bot",
        description="Bot de Cargo Automático 24/7",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Função", value="Atribui cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲' automaticamente", inline=False)
    embed.add_field(name="Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    # Verificar configuração
    cargo = discord.utils.get(ctx.guild.roles, name="𝗩𝗶𝘀𝗶𝘁𝗮𝗧𝗲")
    if cargo:
        embed.add_field(name="Cargo encontrado", value="✅ Sim", inline=True)
    else:
        embed.add_field(name="Cargo encontrado", value="❌ Não (será criado)", inline=True)
    
    embed.set_footer(text="Online 24/7 • Monitorado por UptimeRobot")
    
    await ctx.send(embed=embed)

# ==================== INICIAR TUDO ====================

if __name__ == '__main__':
    # Verificar token PRIMEIRO
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        print("\n❌ DISCORD_TOKEN não encontrado!")
        print("💡 Configure no Render:")
        print("   1. Vá em Environment")
        print("   2. Adicione: DISCORD_TOKEN=seu_token_aqui")
        print("   3. Clique em Save Changes")
        sys.exit(1)
    
    print(f"\n✅ Token encontrado")
    
    # CORREÇÃO: Iniciar servidor web com tratamento de erro
    try:
        start_web_server()
    except Exception as e:
        print(f"⚠️ Erro ao iniciar servidor web: {e}")
        print("💡 Continuando apenas com o bot...")
    
    print("🔗 Conectando ao Discord...")
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido!")
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")
