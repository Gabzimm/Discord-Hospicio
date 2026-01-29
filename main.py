from datetime import datetime
import discord
from discord.ext import commands
import os
import sys
import asyncio
from flask import Flask
from threading import Thread

# ==================== KEEP-ALIVE SERVER ====================
try:
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        from datetime import datetime
        return f"""
        <html>
        <head><title>🤖 Bot Discord</title>
        <meta charset="UTF-8">
        <style>
            body {{font-family: Arial; text-align: center; padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;}}
            .container {{background: rgba(0,0,0,0.8); padding: 30px; border-radius: 15px; max-width: 600px; margin: auto;}}
            .status {{background: #28a745; padding: 15px; border-radius: 10px; margin: 20px 0;}}
        </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot Discord</h1>
                <div class="status">🟢 ONLINE</div>
                <p>Sistema de Cargos Automáticos</p>
                <p><small>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small></p>
            </div>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return "OK", 200
    
    def keep_alive():
        """Inicia servidor web em thread separada"""
        def run():
            app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
        
        t = Thread(target=run, daemon=True)
        t.start()
        print("✅ Servidor web iniciado na porta 8080")
        
except ImportError:
    print("⚠️ Flask não encontrado. Servidor web não será iniciado.")
    def keep_alive():
        pass

# ==================== BOT DISCORD ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== EVENTO DE ENTRADA DE MEMBRO ====================
@bot.event
async def on_member_join(member: discord.Member):
    """Atribui cargo automático quando alguém entra"""
    print(f"👤 {member.name} entrou no servidor!")
    
    try:
        # Buscar cargo "𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞"
        visitante_role = discord.utils.get(member.guild.roles, name="𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞")
        
        if not visitante_role:
            print("❌ Cargo '𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞' não encontrado!")
            
            # Tentar criar automaticamente
            try:
                visitante_role = await member.guild.create_role(
                    name="𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞",
                    color=discord.Color.light_grey(),
                    reason="Criado automaticamente pelo sistema de boas-vindas"
                )
                print(f"✅ Cargo '𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞' criado automaticamente!")
            except discord.Forbidden:
                print("❌ Sem permissão para criar cargo!")
                return
            except Exception as e:
                print(f"❌ Erro ao criar cargo: {e}")
                return
                
        # Dar o cargo ao membro
        await member.add_roles(visitante_role)
        print(f"✅ Cargo '𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞' atribuído a {member.name}")
        
        # Enviar mensagem de boas-vindas
        try:
            canal_entrada = discord.utils.get(member.guild.text_channels, name="🚪entrada")
            
            if not canal_entrada:
                canal_entrada = discord.utils.get(member.guild.text_channels, name="entrada")
            
            if not canal_entrada:
                for channel in member.guild.text_channels:
                    if channel.permissions_for(member.guild.me).send_messages:
                        canal_entrada = channel
                        break
            
            if canal_entrada:
                embed = discord.Embed(
                    title=f"👋 Bem-vindo(a), {member.name}!",
                    description=(
                        f"Seja muito bem-vindo(a) ao **{member.guild.name}**!\n\n"
                        f"👤 **Total de membros:** {member.guild.member_count}\n\n"
                        f"💡 **Para fazer seu set:**\n"
                        f"1. Vá para #Pedir set!\n"
                        f"2. Clique em 'Peça seu Set!'\n"
                        f"3. Digite seu ID do FiveM\n"
                        f"4. E aguarde aprovação da staff!"
                    ),
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                embed.set_footer(text="Seja Bem-vindo!, Esperamos que goste!")
                
                await canal_entrada.send(embed=embed)
                print(f"✅ Mensagem de boas-vindas enviada em #{canal_entrada.name}")
                
        except Exception as e:
            print(f"⚠️ Não foi possível enviar mensagem de boas-vindas: {e}")
        
        print(f"✅ {member.name} recebeu cargo automático")
        
    except discord.Forbidden:
        print(f"❌ Sem permissão para adicionar cargos a {member.name}")
    except Exception as e:
        print(f"❌ Erro no sistema de boas-vindas: {type(e).__name__}: {e}")

# ==================== CARREGAR MÓDULOS ====================
async def load_cogs():
    """Carrega módulos adicionais"""
    print("=" * 50)
    print("🔄 CARREGANDO MÓDULOS...")
    
    # Lista de módulos
    cogs = [
        'modules.tickets',
        'modules.sets',
        'modules.cargos',
    ]
    
    carregados = 0
    for cog in cogs:
        print(f"\n🔍 Tentando: {cog}")
        try:
            await bot.load_extension(cog)
            print(f"✅ '{cog}' carregado!")
            carregados += 1
        except ModuleNotFoundError:
            print(f"⚠️ Módulo não encontrado")
        except ImportError as e:
            print(f"❌ Erro de importação: {e}")
        except Exception as e:
            print(f"❌ Erro: {type(e).__name__}: {e}")
    
    print(f"\n📊 {carregados}/{len(cogs)} módulos carregados")
    print("=" * 50)
    return carregados > 0

# ==================== EVENTOS ====================
@bot.event
async def on_ready():
    print(f'✅ Bot logado como: {bot.user}')
    print(f'🆔 ID: {bot.user.id}')
    print(f'📡 Ping: {round(bot.latency * 1000)}ms')
    print(f'🏠 Servidores: {len(bot.guilds)}')
    print('🚀 Bot pronto!')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidor(es) | !help"
        )
    )
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos slash sincronizados")
    except:
        print("⚠️ Sem comandos slash para sincronizar")

# ==================== COMANDOS ====================
@bot.command()
async def ping(ctx):
    """Mostra latência do bot"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: **{latency}ms**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx):
    """Mostra status do bot"""
    embed = discord.Embed(
        title="🤖 Status do Bot",
        color=discord.Color.green()
    )
    
    embed.add_field(name="🏷️ Nome", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="📡 Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🏠 Servidores", value=len(bot.guilds), inline=True)
    
    total_members = sum(len(g.members) for g in bot.guilds)
    embed.add_field(name="👤 Membros", value=total_members, inline=True)
    
    loaded_cogs = list(bot.cogs.keys())
    embed.add_field(
        name="📦 Módulos", 
        value="\n".join([f"• {cog}" for cog in loaded_cogs]) if loaded_cogs else "Nenhum",
        inline=False
    )
    
    embed.set_footer(text="Online 24/7 com Keep-Alive")
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx):
    """Recarrega módulos"""
    await load_cogs()
    await ctx.send("✅ Módulos recarregados!")

@bot.command()
@commands.has_permissions(administrator=True)
async def test_entrada(ctx):
    """Testa sistema de boas-vindas"""
    await ctx.send("🔧 Testando sistema de boas-vindas...")
    
    canal_entrada = discord.utils.get(ctx.guild.text_channels, name="🚪entrada")
    
    if not canal_entrada:
        canal_entrada = discord.utils.get(ctx.guild.text_channels, name="entrada")
    
    if canal_entrada:
        embed = discord.Embed(
            title="👋 Teste de Boas-vindas",
            description="Esta é uma mensagem de teste!",
            color=discord.Color.blue()
        )
        await canal_entrada.send(embed=embed)
        await ctx.send("✅ Teste enviado!")
    else:
        await ctx.send("❌ Canal de entrada não encontrado")

# ==================== TRATAMENTO DE ERROS ====================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Comando não encontrado. Use `!help`", delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Sem permissão!", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argumentos faltando! Use: `!{ctx.command.name} {ctx.command.signature}`", delete_after=5)
    else:
        print(f"Erro: {error}")

# ==================== INICIALIZAÇÃO ====================
async def main():
    """Função principal"""
    print("🚀 Iniciando bot Discord...")
    print("=" * 50)
    
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ DISCORD_TOKEN não encontrado!")
        print("Configure no Render: Environment → DISCORD_TOKEN")
        sys.exit(1)
    
    # Iniciar servidor web
    keep_alive()
    
    # Carregar módulos
    await load_cogs()
    
    # Iniciar bot
    print("🔗 Conectando ao Discord...")
    await bot.start(TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado")
    except Exception as e:
        print(f"❌ Erro: {e}")
