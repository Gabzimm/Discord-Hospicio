from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os
import sys
import asyncio

# ==================== KEEP-ALIVE SERVER ====================
# ========== SERVIDOR WEB PARA UPTIMEROBOT ==========
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        status = "🟢 ONLINE" if bot.is_ready() else "🟡 CONECTANDO"
        return f"""
        <html>
        <head><title>🤖 Bot Simples</title>
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
                <h1>🤖 Bot Simples</h1>
                <div class="status">{status}</div>
                <p>Cargo Automático + Envio de Mensagens</p>
                <p><small>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small></p>
            </div>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return "OK", 200
    
    def run_web_server():
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    print("✅ Servidor web iniciado na porta 8080")
    
except ImportError:
    print("⚠️ Flask não encontrado. Servidor web não será iniciado.")

# ==================== BOT DISCORD ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # IMPORTANTE para tickets/sets e eventos de membro
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== EVENTO DE ENTRADA DE MEMBRO ====================
@bot.event
async def on_member_join(member: discord.Member):
    """Atribui cargo automático quando alguém entra"""
    print(f"👤 {member.name} entrou no servidor!")
    
    try:
        # 1. Buscar cargo "𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞"
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
                
        # 2. Dar o cargo ao membro
        await member.add_roles(visitante_role)
        print(f"✅ Cargo '𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞' atribuído a {member.name}")
        
        # 3. Enviar mensagem de boas-vindas (opcional)
        try:
            # Correção aqui: usar nome correto da variável e buscar canal
            canal_entrada = discord.utils.get(member.guild.text_channels, name="🚪entrada")
            
            if not canal_entrada:
                # Se não encontrar "🚪entrada", tenta "entrada" sem emoji
                canal_entrada = discord.utils.get(member.guild.text_channels, name="entrada")
            
            if not canal_entrada:
                # Tenta encontrar qualquer canal que o bot possa enviar mensagem
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
        
        # 4. Log no console
        print(f"✅ {member.name} recebeu cargo automático")
        
    except discord.Forbidden:
        print(f"❌ Sem permissão para adicionar cargos a {member.name}")
    except Exception as e:
        print(f"❌ Erro no sistema de boas-vindas: {type(e).__name__}: {e}")

# ==================== CARREGAR SEUS MÓDULOS ====================
async def load_cogs():
    """Carrega seus módulos (tickets, sets, etc.)"""
    print("=" * 50)
    print("🔄 INICIANDO CARREGAMENTO DE MÓDULOS...")
    
    # Verificar se a pasta modules existe
    if not os.path.exists('modules'):
        print("📁 Criando pasta 'modules'...")
        os.makedirs('modules')
    
    print("📁 Conteúdo da pasta 'modules':")
    try:
        for file in os.listdir('modules'):
            print(f"   📄 {file}")
    except:
        print("   ❌ Não foi possível listar arquivos")
    
    # Lista dos SEUS módulos
    cogs = [
        'modules.tickets',
        'modules.sets',
        'modules.cargos',
    ]
    
    carregados = 0
    for cog in cogs:
        print(f"\n🔍 Tentando carregar: {cog}")
        try:
            await bot.load_extension(cog)
            print(f"✅ SUCESSO: Módulo '{cog}' carregado!")
            carregados += 1
        except ModuleNotFoundError as e:
            print(f"❌ ERRO: Módulo não encontrado - {e}")
        except ImportError as e:
            print(f"❌ ERRO: Importação falhou - {e}")
        except commands.ExtensionNotFound:
            print(f"❌ ERRO: Extensão '{cog}' não encontrada")
        except commands.ExtensionFailed as e:
            print(f"❌ ERRO: Extensão falhou - {e.__cause__}")
        except Exception as e:
            print(f"❌ ERRO INESPERADO: {type(e).__name__}: {e}")
    
    print(f"\n📊 Resumo: {carregados}/{len(cogs)} módulos carregados")
    print("=" * 50)
    return carregados > 0

# ==================== EVENTOS ====================
@bot.event
async def on_ready():
    print(f'✅ Bot logado como: {bot.user}')
    print(f'🆔 ID: {bot.user.id}')
    print(f'📡 Ping: {round(bot.latency * 1000)}ms')
    print(f'🏠 Servidores: {len(bot.guilds)}')
    print('🚀 Bot pronto para uso!')
    
    # Atividade personalizada
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidor(es) | !help"
        )
    )
    
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
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: **{latency}ms**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def reload(ctx):
    """Recarrega todos os módulos (apenas dono)"""
    if ctx.author.id != 1213819385576300595:  
        return await ctx.send("❌ Apenas o dono pode usar este comando!")
    
    await load_cogs()
    await ctx.send("✅ Módulos recarregados!")

@bot.command()
async def perms(ctx):
    """Verifica permissões do bot no servidor"""
    perms = ctx.guild.me.guild_permissions
    
    embed = discord.Embed(
        title="🔐 Permissões do Bot",
        description=f"Verificando permissões em {ctx.guild.name}",
        color=discord.Color.blue()
    )
    
    # Permissões importantes
    perms_importantes = [
        ("👑 Gerenciar Cargos", perms.manage_roles, "Para dar cargo automático"),
        ("🏷️ Gerenciar Apelidos", perms.manage_nicknames, "Para mudar nicknames"),
        ("👥 Gerenciar Membros", perms.manage_nicknames, "Para evento on_member_join"),
        ("📁 Gerenciar Canais", perms.manage_channels, "Para tickets"),
        ("📝 Gerenciar Mensagens", perms.manage_messages, "Para sistemas"),
        ("👀 Ver Canais", perms.view_channel, "Básico"),
        ("💬 Enviar Mensagens", perms.send_messages, "Básico"),
        ("📜 Ler Histórico", perms.read_message_history, "Para tickets"),
    ]
    
    for name, has_perm, desc in perms_importantes:
        status = "✅" if has_perm else "❌"
        embed.add_field(
            name=f"{status} {name}",
            value=desc,
            inline=False
        )
    
    # Verificar posição do cargo do bot
    bot_role = ctx.guild.me.top_role
    embed.add_field(
        name="📊 Posição do Cargo do Bot",
        value=f"**Cargo:** `{bot_role.name}`\n**Posição:** {bot_role.position}/{len(ctx.guild.roles)}\n\n⚠️ **O cargo do bot deve estar ACIMA dos cargos que ele gerencia!**",
        inline=False
    )
    
    # Verificar intents
    embed.add_field(
        name="🔧 Intents Ativos",
        value=f"• Members Intent: {'✅' if bot.intents.members else '❌'}\n• Message Content: {'✅' if bot.intents.message_content else '❌'}",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx):
    """Mostra status completo do bot"""
    embed = discord.Embed(
        title="🤖 Status do Bot",
        description=f"Informações de {bot.user.name}",
        color=discord.Color.green()
    )
    
    embed.add_field(name="🏷️ Nome", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="📡 Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🏠 Servidores", value=len(bot.guilds), inline=True)
    
    # Contar membros totais
    total_members = sum(len(g.members) for g in bot.guilds)
    embed.add_field(name="👤 Membros Totais", value=total_members, inline=True)
    
    # Módulos carregados
    loaded_cogs = list(bot.cogs.keys())
    embed.add_field(
        name="📦 Módulos Ativos", 
        value="\n".join([f"• {cog}" for cog in loaded_cogs]) if loaded_cogs else "Nenhum módulo carregado",
        inline=False
    )
    
    # Uptime (aproximado)
    embed.set_footer(text="Sistema Hospício APP • Online 24/7")
    
    await ctx.send(embed=embed)

@bot.command()
async def setup_all(ctx):
    """Configura todos os sistemas de uma vez (apenas ADM)"""
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ Apenas administradores podem usar este comando!")
    
    await ctx.send("🔄 Configurando todos os sistemas...")
    
    # 1. Setup Cargos
    try:
        cargos_cog = bot.get_cog("CargosCog")
        if cargos_cog:
            await ctx.invoke(bot.get_command("setup_cargos"))
            await asyncio.sleep(1)
    except:
        pass
    
    # 2. Setup Set
    try:
        sets_cog = bot.get_cog("SetsCog")
        if sets_cog:
            await ctx.invoke(bot.get_command("setup_set"))
            await asyncio.sleep(1)
    except:
        pass
    
    # 3. Setup Tickets
    try:
        tickets_cog = bot.get_cog("TicketsCog")
        if tickets_cog:
            await ctx.invoke(bot.get_command("setup_tickets"))
            await asyncio.sleep(1)
    except:
        pass
    
    await ctx.send("✅ Todos os sistemas foram configurados!")

@bot.command()
async def test_entrada(ctx):
    """Testa o sistema de boas-vindas (apenas ADM)"""
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ Apenas administradores podem usar este comando!")
    
    # Simular um membro entrando
    await ctx.send("🔧 Testando sistema de boas-vindas...")
    
    # Buscar canal de entrada
    canal_entrada = discord.utils.get(ctx.guild.text_channels, name="🚪entrada")
    
    if not canal_entrada:
        canal_entrada = discord.utils.get(ctx.guild.text_channels, name="entrada")
    
    if canal_entrada:
        await ctx.send(f"✅ Canal de entrada encontrado: {canal_entrada.mention}")
        
        # Testar mensagem
        embed = discord.Embed(
            title="👋 Teste de Boas-vindas",
            description="Esta é uma mensagem de teste do sistema de boas-vindas!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Canal", value=canal_entrada.mention, inline=True)
        embed.add_field(name="Status", value="✅ Funcionando", inline=True)
        
        await canal_entrada.send(embed=embed)
        await ctx.send("✅ Mensagem de teste enviada com sucesso!")
    else:
        await ctx.send("❌ Canal '🚪entrada' não encontrado! Canais disponíveis:")
        for channel in ctx.guild.text_channels:
            await ctx.send(f"• #{channel.name}")

# ==================== INICIALIZAÇÃO ====================
if __name__ == '__main__':
    print("🚀 Iniciando bot Discord...")
    print("=" * 50)
    
    # Verificar token
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("💡 Configure em: Render Dashboard → Environment → Add Variable")
        print("💡 Ou crie um arquivo .env com: DISCORD_TOKEN=seu_token")
        sys.exit(1)
    
    print("✅ Token encontrado")
    print(f"🤖 Nome do Bot: {bot.user if hasattr(bot, 'user') else 'Carregando...'}")
    
    # Iniciar keep-alive
    keep_alive()
    
    # Carregar SEUS módulos antes de iniciar
    async def startup():
        success = await load_cogs()
        if not success:
            print("⚠️  Alguns módulos não foram carregados, continuando...")
    
    # Executar carregamento
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(startup())
    
    # Iniciar bot
    try:
        print("🔗 Conectando ao Discord...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido ou expirado!")
        print("💡 Gere um novo token em: https://discord.com/developers/applications")
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {type(e).__name__}: {e}")
