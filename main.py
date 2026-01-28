"""
🤖 BOT SIMPLES DE CARGO AUTOMÁTICO + ENVIO DE MENSAGENS
Funcionalidades:
1. Atribui cargo "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲" automaticamente
2. Painel básico para envio de mensagens
"""

import os
import sys
import json
from threading import Thread
from datetime import datetime

# ========== CONFIGURAÇÃO DO BOT ==========
print("=" * 50)
print("🚀 INICIANDO BOT SIMPLES")
print("=" * 50)

# Tentar importar discord.py
try:
    import discord
    from discord.ext import commands
    print("✅ discord.py importado com sucesso")
except ImportError:
    print("❌ discord.py não encontrado!")
    print("💡 Instale com: pip install discord.py==2.3.2")
    sys.exit(1)

# Configurar intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

# Criar bot
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

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

# ========== SISTEMA DE MENSAGENS SIMPLES ==========

def criar_embed_mensagem(titulo: str, conteudo: str, cor: str = "#3498db") -> discord.Embed:
    """Cria embed para mensagem"""
    try:
        color = discord.Color.from_str(cor)
    except:
        color = discord.Color.blue()
    
    embed = discord.Embed(
        title=titulo,
        description=conteudo,
        color=color,
        timestamp=datetime.now()
    )
    embed.set_footer(text="📢 Sistema de Mensagens")
    return embed

# ========== EVENTOS DO BOT ==========

@bot.event
async def on_ready():
    """Quando o bot conecta ao Discord"""
    print("=" * 50)
    print(f"✅ BOT CONECTADO: {bot.user.name}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print(f"🏠 Servidores conectados: {len(bot.guilds)}")
    print("=" * 50)
    
    # Configurar painel em cada servidor
    for guild in bot.guilds:
        await configurar_painel(guild)
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"👥 {sum(g.member_count for g in bot.guilds)} membros"
        )
    )
    
    print("🎯 Bot pronto! (Cargo automático + Painel básico)")

@bot.event
async def on_member_join(member):
    """
    ATRIBUI CARGO AUTOMATICAMENTE QUANDO ALGUÉM ENTRA
    """
    print(f"\n{'='*50}")
    print(f"👤 NOVO MEMBRO: {member.name}")
    
    try:
        cargo_nome = "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲"
        cargo = discord.utils.get(member.guild.roles, name=cargo_nome)
        
        if not cargo:
            print(f"⚠️ Cargo '{cargo_nome}' não encontrado. Criando...")
            cargo = await member.guild.create_role(
                name=cargo_nome,
                color=discord.Color.light_grey(),
                reason="Criado automaticamente pelo bot",
                permissions=discord.Permissions.none()
            )
            print(f"✅ Cargo '{cargo_nome}' criado!")
        
        await member.add_roles(cargo)
        print(f"✅ Cargo atribuído a {member.name}")
        
    except Exception as e:
        print(f"❌ Erro ao atribuir cargo: {e}")
    
    print(f"{'='*50}")

async def configurar_painel(guild: discord.Guild):
    """Configura o painel no canal especificado"""
    canal_painel = discord.utils.get(guild.text_channels, name="𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚")
    
    if canal_painel:
        # Limpar mensagens antigas do bot
        try:
            async for message in canal_painel.history(limit=10):
                if message.author == bot.user:
                    await message.delete()
        except:
            pass
        
        # Enviar novo painel
        await enviar_painel_principal(canal_painel)
        print(f"✅ Painel configurado em #{canal_painel.name}")
    else:
        print(f"⚠️ Canal '𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚' não encontrado em {guild.name}")

async def enviar_painel_principal(canal: discord.TextChannel):
    """Envia o painel principal"""
    embed = discord.Embed(
        title="📢 **PAINEL DE MENSAGENS SIMPLES**",
        description=(
            "**Sistema básico para envio de mensagens**\n\n"
            "🎯 **Funcionalidades:**\n"
            "• 📝 **Enviar mensagem** para canais\n"
            "• 📋 **Templates** prontos para usar\n"
            "• 👁️ **Pré-visualização** antes de enviar\n\n"
            "**Clique nos botões abaixo:**"
        ),
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="⚡ **Comandos Rápidos**",
        value=(
            "• `!enviar <canal> <mensagem>` - Envia mensagem\n"
            "• `!painel` - Recarrega este painel\n"
            "• `!ping` - Verifica status do bot"
        ),
        inline=False
    )
    
    embed.set_footer(text="Bot Simples • Online 24/7")
    
    view = PainelSimplesView()
    await canal.send(embed=embed, view=view)

# ========== CLASSES DO PAINEL SIMPLES ==========

class PainelSimplesView(discord.ui.View):
    """View principal do painel simples"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📝 Enviar Mensagem", style=discord.ButtonStyle.primary, emoji="📝")
    async def enviar_mensagem(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Abre modal para enviar mensagem"""
        modal = ModalEnviarMensagemSimples()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Templates", style=discord.ButtonStyle.green, emoji="📋")
    async def usar_template(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mostra templates disponíveis"""
        embed = discord.Embed(
            title="📋 **Templates Disponíveis**",
            description="Selecione um template para usar:",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📢 Anúncio Importante",
            value="`!template anuncio <titulo> <conteudo>`",
            inline=False
        )
        
        embed.add_field(
            name="🎉 Evento",
            value="`!template evento <nome> <descricao> <data>`",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Aviso",
            value="`!template aviso <mensagem>`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❓ Ajuda", style=discord.ButtonStyle.secondary, emoji="❓")
    async def ajuda(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mostra ajuda"""
        await interaction.response.send_message(
            "**❓ Ajuda - Painel Simples**\n\n"
            "**Como usar:**\n"
            "1. Clique em **📝 Enviar Mensagem**\n"
            "2. Preencha o formulário\n"
            "3. Selecione os canais\n"
            "4. Confirme o envio\n\n"
            "**Comandos:**\n"
            "• `!enviar #canal mensagem`\n"
            "• `!painel` - Recarrega painel\n"
            "• `!ping` - Status do bot",
            ephemeral=True
        )

class ModalEnviarMensagemSimples(discord.ui.Modal, title="📝 Enviar Mensagem"):
    """Modal simples para enviar mensagem"""
    
    titulo = discord.ui.TextInput(
        label="Título da mensagem:",
        placeholder="Ex: Anúncio Importante",
        required=True,
        max_length=100
    )
    
    conteudo = discord.ui.TextInput(
        label="Conteúdo:",
        placeholder="Digite sua mensagem aqui...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Mostrar pré-visualização
        embed = criar_embed_mensagem(
            self.titulo.value,
            self.conteudo.value
        )
        
        # Criar view para selecionar canais
        view = SelecaoCanaisSimplesView(self.titulo.value, self.conteudo.value)
        
        await interaction.followup.send(
            "👁️ **Pré-visualização:**",
            embed=embed,
            view=view,
            ephemeral=True
        )

class SelecaoCanaisSimplesView(discord.ui.View):
    """View simples para selecionar canais"""
    
    def __init__(self, titulo: str, conteudo: str):
        super().__init__()
        self.titulo = titulo
        self.conteudo = conteudo
        self.canais_selecionados = []
    
    @discord.ui.select(
        placeholder="📂 Selecione os canais...",
        min_values=1,
        max_values=10,  # Máximo 10 canais
        options=[]  # Será preenchido dinamicamente
    )
    async def select_canais(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Quando canais são selecionados"""
        self.canais_selecionados = [int(canal_id) for canal_id in select.values]
        
        # Criar botão de confirmação
        view_confirmar = ViewConfirmarEnvio(
            self.titulo,
            self.conteudo,
            self.canais_selecionados
        )
        
        await interaction.response.edit_message(
            content=f"✅ {len(self.canais_selecionados)} canal(is) selecionado(s)!",
            view=view_confirmar
        )
    
    async def on_timeout(self):
        """Quando o view expira"""
        pass

class ViewConfirmarEnvio(discord.ui.View):
    """View para confirmar envio"""
    
    def __init__(self, titulo: str, conteudo: str, canais_ids: list):
        super().__init__()
        self.titulo = titulo
        self.conteudo = conteudo
        self.canais_ids = canais_ids
    
    @discord.ui.button(label="✅ Confirmar Envio", style=discord.ButtonStyle.green, emoji="✅")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirma e envia a mensagem"""
        await interaction.response.defer(ephemeral=True)
        
        sucesso = 0
        falhas = 0
        
        for canal_id in self.canais_ids:
            try:
                canal = interaction.guild.get_channel(canal_id)
                if canal and isinstance(canal, discord.TextChannel):
                    embed = criar_embed_mensagem(self.titulo, self.conteudo)
                    await canal.send(embed=embed)
                    sucesso += 1
                else:
                    falhas += 1
            except:
                falhas += 1
        
        await interaction.followup.send(
            f"✅ Mensagem enviada para {sucesso} canal(is)! "
            f"{f'({falhas} falhas)' if falhas > 0 else ''}",
            ephemeral=True
        )
    
    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancela o envio"""
        await interaction.response.edit_message(
            content="❌ Envio cancelado!",
            view=None
        )

# ========== COMANDOS DO BOT ==========

@bot.command(name="painel")
@commands.has_permissions(administrator=True)
async def comando_painel(ctx):
    """Recarrega o painel de mensagens"""
    await ctx.message.delete()
    await configurar_painel(ctx.guild)
    await ctx.send("✅ Painel recarregado!", delete_after=5)

@bot.command(name="enviar")
@commands.has_permissions(manage_messages=True)
async def comando_enviar(ctx, canal: discord.TextChannel, *, mensagem: str):
    """Envia uma mensagem para um canal específico"""
    try:
        embed = discord.Embed(
            title=f"Mensagem de {ctx.author.name}",
            description=mensagem,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Enviado por {ctx.author}")
        
        await canal.send(embed=embed)
        await ctx.send(f"✅ Mensagem enviada para {canal.mention}!")
    except Exception as e:
        await ctx.send(f"❌ Erro ao enviar mensagem: {e}")

@bot.command(name="template")
@commands.has_permissions(manage_messages=True)
async def comando_template(ctx, tipo: str, *, conteudo: str):
    """Usa um template para enviar mensagem"""
    tipos_validos = {
        "anuncio": ("📢 ANÚNCIO IMPORTANTE", "#FF0000"),
        "evento": ("🎉 EVENTO", "#00FF00"),
        "aviso": ("⚠️ AVISO", "#FFA500")
    }
    
    if tipo.lower() not in tipos_validos:
        await ctx.send(f"❌ Tipo inválido! Use: {', '.join(tipos_validos.keys())}")
        return
    
    titulo, cor = tipos_validos[tipo.lower()]
    
    # Criar view para selecionar canais
    class ViewTemplate(discord.ui.View):
        @discord.ui.select(
            placeholder="📂 Selecione os canais...",
            min_values=1,
            max_values=5,
            options=[
                discord.SelectOption(label="#geral", value="geral"),
                discord.SelectOption(label="#anúncios", value="anuncios"),
                discord.SelectOption(label="#eventos", value="eventos")
            ]
        )
        async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
            await interaction.response.defer()
            
            # Enviar para os canais selecionados
            for opcao in select.values:
                if opcao == "geral":
                    canal = discord.utils.get(ctx.guild.text_channels, name="geral")
                elif opcao == "anuncios":
                    canal = discord.utils.get(ctx.guild.text_channels, name="anúncios")
                elif opcao == "eventos":
                    canal = discord.utils.get(ctx.guild.text_channels, name="eventos")
                else:
                    continue
                
                if canal:
                    embed = discord.Embed(
                        title=titulo,
                        description=conteudo,
                        color=discord.Color.from_str(cor),
                        timestamp=datetime.now()
                    )
                    embed.set_footer(text="📢 Sistema de Templates")
                    await canal.send(embed=embed)
            
            await interaction.followup.send(f"✅ Template enviado para {len(select.values)} canal(is)!", ephemeral=True)
    
    embed = discord.Embed(
        title=titulo,
        description=conteudo,
        color=discord.Color.from_str(cor)
    )
    
    await ctx.send("👁️ **Pré-visualização do template:**", embed=embed)
    await ctx.send("**📂 Selecione os canais para enviar:**", view=ViewTemplate())

@bot.command(name="ping")
async def comando_ping(ctx):
    """Verifica se o bot está online"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot online e funcionando! 🎯",
        color=discord.Color.green()
    )
    embed.add_field(name="📡 Ping", value=f"{latency}ms", inline=True)
    embed.add_field(name="🏠 Servidores", value=f"{len(bot.guilds)}", inline=True)
    embed.add_field(name="👥 Membros", value=f"{sum(g.member_count for g in bot.guilds)}", inline=True)
    embed.set_footer(text="Bot Simples • Online 24/7")
    
    await ctx.send(embed=embed)

@bot.command(name="status")
async def comando_status(ctx):
    """Mostra status completo do bot"""
    embed = discord.Embed(
        title="🤖 Status do Bot",
        description="Informações do sistema",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Nome", value=bot.user.name, inline=True)
    embed.add_field(name="ID", value=bot.user.id, inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="Membros totais", value=f"{sum(g.member_count for g in bot.guilds)}", inline=True)
    embed.add_field(name="Online desde", value=bot.user.created_at.strftime('%d/%m/%Y'), inline=True)
    
    # Verificar permissões
    perms = ctx.guild.me.guild_permissions
    tem_permissao = "✅ SIM" if perms.manage_roles else "❌ NÃO"
    embed.add_field(name="Pode gerenciar cargos?", value=tem_permissao, inline=True)
    
    # Cargo visitante
    cargo_visitante = discord.utils.get(ctx.guild.roles, name="𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲")
    if cargo_visitante:
        embed.add_field(
            name="Cargo visitante",
            value=f"{cargo_visitante.mention} está configurado",
            inline=False
        )
    else:
        embed.add_field(
            name="Cargo visitante",
            value="❌ Não encontrado (será criado automaticamente)",
            inline=False
        )
    
    embed.set_footer(text="Use !ping para testar • !ajuda para ajuda completa")
    await ctx.send(embed=embed)

@bot.command(name="ajuda")
async def comando_ajuda(ctx):
    """Mostra ajuda completa"""
    embed = discord.Embed(
        title="📚 **Ajuda - Bot Simples**",
        description="Sistema básico de cargo automático + envio de mensagens",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="🎯 **Funcionalidades**",
        value=(
            "1. **Cargo Automático** - Atribui '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲' automaticamente\n"
            "2. **Painel de Mensagens** - Interface no canal `𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚`\n"
            "3. **Envio Simples** - Botões para enviar mensagens\n"
            "4. **Templates** - Modelos prontos para usar"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📋 **Comandos**",
        value=(
            "• `!ping` - Status do bot\n"
            "• `!status` - Status completo\n"
            "• `!painel` - Recarrega painel (admin)\n"
            "• `!enviar #canal mensagem` - Envia mensagem\n"
            "• `!template <tipo> <conteudo>` - Usa template\n"
            "• `!ajuda` - Esta mensagem"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ **Configuração**",
        value=(
            "1. Crie o canal `𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚`\n"
            "2. Use `!painel` para configurar\n"
            "3. Dê permissão 'Gerenciar Cargos' ao bot"
        ),
        inline=False
    )
    
    embed.set_footer(text="Bot Online 24/7 • Hospedado no Render")
    await ctx.send(embed=embed)

# ========== EVENTO QUANDO BOT É ADICIONADO ==========

@bot.event
async def on_guild_join(guild):
    """Quando o bot é adicionado a um novo servidor"""
    print(f"\n{'='*50}")
    print(f"🏠 NOVO SERVIDOR: {guild.name}")
    print(f"{'='*50}")
    
    # Configurar painel automaticamente
    await configurar_painel(guild)
    
    # Tentar enviar mensagem de boas-vindas
    try:
        canal_geral = discord.utils.get(guild.text_channels, name="geral")
        if not canal_geral:
            for canal in guild.text_channels:
                if canal.permissions_for(guild.me).send_messages:
                    canal_geral = canal
                    break
        
        if canal_geral:
            embed = discord.Embed(
                title="🤖 Bot Adicionado com Sucesso!",
                description=(
                    "Olá! Fui adicionado ao servidor com **duas funções principais:**\n\n"
                    "🎯 **1. Cargo Automático**\n"
                    "• Atribui `𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲` a novos membros\n"
                    "• Cria o cargo automaticamente se não existir\n\n"
                    "📢 **2. Painel de Mensagens**\n"
                    "• Sistema básico no canal `𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚`\n"
                    "• Envie mensagens facilmente\n"
                    "• Use templates prontos\n\n"
                    "⚡ **Comandos rápidos:**\n"
                    "• `!painel` - Configura o painel\n"
                    "• `!ajuda` - Ajuda completa"
                ),
                color=discord.Color.green()
            )
            
            await canal_geral.send(embed=embed)
    except:
        pass

# ========== FUNÇÃO PARA ATUALIZAR SELECT DE CANAIS ==========

@bot.event
async def on_interaction(interaction: discord.Interaction):
    """Intercepta interações para atualizar selects dinamicamente"""
    if interaction.type == discord.InteractionType.component:
        # Se for um select de canais, atualizar opções
        if hasattr(interaction.data, 'custom_id') and 'select_canais' in interaction.data.get('custom_id', ''):
            await atualizar_opcoes_canais(interaction)

async def atualizar_opcoes_canais(interaction: discord.Interaction):
    """Atualiza as opções do select com os canais do servidor"""
    try:
        # Obter todos os canais de texto
        canais = [c for c in interaction.guild.text_channels if c.permissions_for(interaction.guild.me).send_messages]
        
        # Limitar a 25 canais (limite do Discord)
        canais = canais[:25]
        
        # Criar opções
        options = []
        for canal in canais:
            options.append(
                discord.SelectOption(
                    label=f"#{canal.name}"[:100],
                    value=str(canal.id),
                    description=f"Enviar para #{canal.name}"[:100]
                )
            )
        
        # Atualizar a view
        view = discord.ui.View()
        select = discord.ui.Select(
            placeholder="📂 Selecione os canais...",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="select_canais"
        )
        select.callback = lambda i, s: handle_canal_selection(i, s)
        view.add_item(select)
        
        await interaction.response.edit_message(view=view)
    except:
        pass

async def handle_canal_selection(interaction: discord.Interaction, select: discord.ui.Select):
    """Lida com a seleção de canais"""
    await interaction.response.defer()

# ========== INICIAR BOT ==========

if __name__ == "__main__":
    # OBTER TOKEN DO BOT
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    if not TOKEN:
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("DISCORD_TOKEN="):
                        TOKEN = line.split("=")[1].strip()
                        break
        except:
            pass
    
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("\n💡 COMO CONFIGURAR NO RENDER:")
        print("1. No painel do Render, vá em Environment")
        print("2. Adicione a variável:")
        print("   Key: DISCORD_TOKEN")
        print("   Value: seu_token_do_bot")
        print("\n🔗 Obtenha seu token em: https://discord.com/developers/applications")
        sys.exit(1)
    
    print("✅ Token encontrado")
    print("🔗 Conectando ao Discord...")
    print("=" * 50)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido ou expirado!")
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado manualmente")
    except Exception as e:
        print(f"❌ ERRO: {type(e).__name__}: {e}")
