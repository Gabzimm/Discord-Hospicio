from datetime import datetime
import discord
from discord.ext import commands
import os
import sys
import asyncio
from aiohttp import web
import threading

# ==================== KEEP-ALIVE SERVER (aiohttp) ====================
class KeepAliveServer:
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.setup_routes()
        self.runner = None
        self.site = None
    
    def setup_routes(self):
        self.app.router.add_get('/', self.handle_root)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/status', self.handle_status)
    
    async def handle_root(self, request):
        """Página principal HTML"""
        status = "🟢 ONLINE" if self.bot.is_ready() else "🟡 CONECTANDO"
        latency = f"{round(self.bot.latency * 1000)}ms" if self.bot.is_ready() else "0ms"
        
        html = f"""
        <html>
        <head>
            <title>🤖 Bot Discord</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    text-align: center;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                }}
                .container {{
                    background: rgba(0, 0, 0, 0.85);
                    padding: 40px;
                    border-radius: 20px;
                    max-width: 800px;
                    margin: 50px auto;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                    backdrop-filter: blur(10px);
                }}
                .status {{
                    background: #28a745;
                    padding: 20px;
                    border-radius: 15px;
                    margin: 30px 0;
                    font-size: 1.5em;
                    font-weight: bold;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .info-card {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #667eea;
                }}
                .info-card h3 {{
                    margin-top: 0;
                    color: #ffcc00;
                }}
                footer {{
                    margin-top: 40px;
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 0.9em;
                }}
                h1 {{
                    color: #ffcc00;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot Discord</h1>
                <div class="status">{status}</div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <h3>📊 Status</h3>
                        <p>Latência: {latency}</p>
                        <p>Bot: {str(self.bot.user) if self.bot.user else "Conectando..."}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>🏠 Servidores</h3>
                        <p>{len(self.bot.guilds)} servidor(es)</p>
                        <p>{sum(len(g.members) for g in self.bot.guilds)} membros</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>🔧 Sistema</h3>
                        <p>Cargos Automáticos</p>
                        <p>Tickets & Sets</p>
                    </div>
                </div>
                
                <p><strong>Sistema de cargos automáticos + Tickets</strong></p>
                
                <footer>
                    <p>🚀 Mantido online 24/7</p>
                    <p><small>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small></p>
                    <p><small>Health check: <a href="/health" style="color: #4dabf7;">/health</a> | Status JSON: <a href="/status" style="color: #4dabf7;">/status</a></small></p>
                </footer>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def handle_health(self, request):
        """Endpoint de health check simples"""
        return web.Response(text="OK", status=200)
    
    async def handle_status(self, request):
        """Endpoint JSON com status detalhado"""
        status_data = {
            "status": "online" if self.bot.is_ready() else "starting",
            "bot": {
                "name": str(self.bot.user) if self.bot.user else None,
                "id": str(self.bot.user.id) if self.bot.user else None
            },
            "server": {
                "guilds": len(self.bot.guilds),
                "total_members": sum(len(g.members) for g in self.bot.guilds) if self.bot.is_ready() else 0,
                "latency": f"{round(self.bot.latency * 1000)}ms" if self.bot.is_ready() else "0ms"
            },
            "system": {
                "cogs_loaded": len(self.bot.cogs),
                "cogs_list": list(self.bot.cogs.keys()),
                "uptime": str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            },
            "endpoints": {
                "health": "/health",
                "status": "/status",
                "root": "/"
            }
        }
        return web.json_response(status_data)
    
    async def start(self, port=8080):
        """Inicia o servidor web"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', port)
        await self.site.start()
        print(f"🌐 Servidor keep-alive iniciado na porta {port}")
        print(f"📊 Health check: http://0.0.0.0:{port}/health")
        print(f"📈 Status JSON: http://0.0.0.0:{port}/status")
        print(f"🏠 Página web: http://0.0.0.0:{port}/")
    
    async def stop(self):
        """Para o servidor web"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        print("🛑 Servidor keep-alive parado")

# ==================== BOT DISCORD ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
keep_alive_server = None

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
    
    # Status do keep-alive
    if keep_alive_server and keep_alive_server.site:
        embed.add_field(
            name="🌐 Keep-Alive",
            value="✅ Ativo\nPorta: 8080\nHealth check: /health",
            inline=False
        )
    
    embed.set_footer(text="Online 24/7 com Keep-Alive")
    
    await ctx.send(embed=embed)

@bot.command(name='keepalive')
@commands.has_permissions(administrator=True)
async def keepalive_status(ctx):
    """Mostra status do servidor keep-alive"""
    embed = discord.Embed(
        title="🌐 Status Keep-Alive",
        color=discord.Color.blue()
    )
    
    if keep_alive_server and keep_alive_server.site:
        embed.description = "✅ Servidor keep-alive está ativo"
        embed.add_field(name="Porta", value="8080", inline=True)
        embed.add_field(name="Status", value="🟢 ONLINE", inline=True)
        embed.add_field(name="IP", value="0.0.0.0", inline=True)
        embed.add_field(name="Endpoints", 
                       value="[🌐 Página Web](http://0.0.0.0:8080/)\n[📊 Health Check](http://0.0.0.0:8080/health)\n[📈 Status JSON](http://0.0.0.0:8080/status)",
                       inline=False)
    else:
        embed.description = "❌ Servidor keep-alive não está ativo"
    
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
    
    # Inicializar servidor keep-alive
    global keep_alive_server
    keep_alive_server = KeepAliveServer(bot)
    
    try:
        # Iniciar servidor web
        print("🌐 Iniciando servidor keep-alive...")
        await keep_alive_server.start(8080)
    except Exception as e:
        print(f"⚠️ Erro ao iniciar servidor keep-alive: {e}")
        print("⚠️ Continuando sem servidor web...")
        keep_alive_server = None
    
    # Carregar módulos
    await load_cogs()
    
    # Iniciar bot
    print("🔗 Conectando ao Discord...")
    try:
        await bot.start(TOKEN)
    finally:
        # Garantir que o servidor web seja parado corretamente
        if keep_alive_server:
            await keep_alive_server.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado pelo usuário")
        if keep_alive_server:
            asyncio.run(keep_alive_server.stop())
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
