import discord
from discord.ext import commands
import os

# ========== CONFIGURAÇÕES ==========
intents = discord.Intents.default()
intents.members = True  # ✅ OBRIGATÓRIO para on_member_join
intents.message_content = True  # ✅ Para comandos

bot = commands.Bot(command_prefix="!", intents=intents)

# ⚠️ SUBSTITUA PELO ID REAL DO CARGO "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨"
CARGO_ID = 1460747749241913434  # ← COLOCA O ID AQUI!

# ========== EVENTOS ==========
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"🆔 ID do Bot: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    
    # Verificar se cargo existe
    for guild in bot.guilds:
        cargo = guild.get_role(CARGO_ID)
        if cargo:
            print(f"✅ Cargo encontrado: {cargo.name} (ID: {cargo.id})")
        else:
            print(f"❌ Cargo com ID {CARGO_ID} NÃO encontrado no servidor {guild.name}")

@bot.event
async def on_member_join(member):
    print(f"🎯 {member.name} entrou no servidor!")
    
    try:
        # Buscar cargo pelo ID
        cargo = member.guild.get_role(CARGO_ID)
        
        if not cargo:
            print(f"❌ Cargo com ID {CARGO_ID} não encontrado!")
            return
        
        print(f"✅ Cargo encontrado: {cargo.name}")
        
        # Verificar permissões do bot
        bot_member = member.guild.get_member(bot.user.id)
        if not bot_member.guild_permissions.manage_roles:
            print("❌ Bot SEM permissão 'Gerenciar Cargos'")
            return
        
        # Verificar hierarquia
        bot_top_role = bot_member.top_role
        if bot_top_role.position <= cargo.position:
            print(f"❌ Hierarquia: Bot role ({bot_top_role.position}) ≤ Cargo ({cargo.position})")
            print(f"💡 Solução: Arraste o cargo do bot ACIMA do cargo {cargo.name}")
            return
        
        # Dar o cargo
        await member.add_roles(cargo, reason="Auto-role: entrada no servidor")
        print(f"✅ Cargo '{cargo.name}' dado para {member.name}")
        
        # Log no console
        print(f"📝 {member.name} recebeu o cargo {cargo.name}")
        
    except discord.Forbidden:
        print("❌ PERMISSÃO NEGADA: Bot não pode dar este cargo")
    except Exception as e:
        print(f"❌ ERRO: {type(e).__name__}: {e}")

# ========== COMANDOS DE TESTE ==========
@bot.command()
async def test_autorole(ctx, member: discord.Member = None):
    """Testa o sistema de auto-role"""
    if member is None:
        member = ctx.author
    
    cargo = ctx.guild.get_role(CARGO_ID)
    
    if not cargo:
        await ctx.send(f"❌ Cargo com ID `{CARGO_ID}` não encontrado!")
        return
    
    try:
        await member.add_roles(cargo)
        await ctx.send(f"✅ Teste OK! Cargo {cargo.mention} dado para {member.mention}")
    except Exception as e:
        await ctx.send(f"❌ Erro: `{type(e).__name__}: {e}`")

@bot.command()
async def autorole_info(ctx):
    """Mostra informações do sistema de auto-role"""
    cargo = ctx.guild.get_role(CARGO_ID)
    
    embed = discord.Embed(
        title="🛬 Sistema de Auto-Role",
        color=discord.Color.blue()
    )
    
    if cargo:
        embed.description = f"**Cargo alvo:** {cargo.mention} (`{cargo.id}`)"
        embed.add_field(name="🎨 Cor", value=str(cargo.color), inline=True)
        embed.add_field(name="👥 Membros", value=len(cargo.members), inline=True)
        embed.add_field(name="📊 Posição", value=f"#{cargo.position}", inline=True)
        
        # Verificar permissões
        bot_member = ctx.guild.get_member(bot.user.id)
        if bot_member.guild_permissions.manage_roles:
            embed.add_field(name="✅ Permissão", value="Gerenciar Cargos", inline=True)
        else:
            embed.add_field(name="❌ Permissão", value="Falta: Gerenciar Cargos", inline=True)
        
        # Verificar hierarquia
        bot_top_role = bot_member.top_role
        if bot_top_role.position > cargo.position:
            embed.add_field(name="✅ Hierarquia", value="Bot acima do cargo", inline=True)
        else:
            embed.add_field(name="❌ Hierarquia", value="Bot abaixo do cargo", inline=True)
            
        embed.set_footer(text="Status: Ativo ✅")
    else:
        embed.description = f"❌ Cargo com ID `{CARGO_ID}` não encontrado!"
        embed.add_field(
            name="🆔 Como encontrar o ID:",
            value="1. Ative Modo Desenvolvedor\n2. Clique direito no cargo → Copiar ID",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def set_cargo_id(ctx, novo_id: int):
    """Define um novo ID de cargo para auto-role"""
    global CARGO_ID
    CARGO_ID = novo_id
    
    cargo = ctx.guild.get_role(CARGO_ID)
    if cargo:
        await ctx.send(f"✅ Auto-role configurado para: {cargo.mention} (`{cargo.id}`)")
    else:
        await ctx.send(f"⚠️ ID `{novo_id}` definido, mas cargo não encontrado")

# ========== INICIAR BOT ==========
if __name__ == "__main__":
    # Lê o token da variável de ambiente
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("💡 Configure a variável de ambiente ou coloque o token diretamente")
        exit(1)
    
    print("🚀 Iniciando bot...")
    bot.run(TOKEN)import discord
from discord.ext import commands
import os

# ========== CONFIGURAÇÕES ==========
intents = discord.Intents.default()
intents.members = True  # ✅ OBRIGATÓRIO para on_member_join
intents.message_content = True  # ✅ Para comandos

bot = commands.Bot(command_prefix="!", intents=intents)

# ⚠️ SUBSTITUA PELO ID REAL DO CARGO "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨"
CARGO_ID = 123456789012345678  # ← COLOCA O ID AQUI!

# ========== EVENTOS ==========
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"🆔 ID do Bot: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    
    # Verificar se cargo existe
    for guild in bot.guilds:
        cargo = guild.get_role(CARGO_ID)
        if cargo:
            print(f"✅ Cargo encontrado: {cargo.name} (ID: {cargo.id})")
        else:
            print(f"❌ Cargo com ID {CARGO_ID} NÃO encontrado no servidor {guild.name}")

@bot.event
async def on_member_join(member):
    print(f"🎯 {member.name} entrou no servidor!")
    
    try:
        # Buscar cargo pelo ID
        cargo = member.guild.get_role(CARGO_ID)
        
        if not cargo:
            print(f"❌ Cargo com ID {CARGO_ID} não encontrado!")
            return
        
        print(f"✅ Cargo encontrado: {cargo.name}")
        
        # Verificar permissões do bot
        bot_member = member.guild.get_member(bot.user.id)
        if not bot_member.guild_permissions.manage_roles:
            print("❌ Bot SEM permissão 'Gerenciar Cargos'")
            return
        
        # Verificar hierarquia
        bot_top_role = bot_member.top_role
        if bot_top_role.position <= cargo.position:
            print(f"❌ Hierarquia: Bot role ({bot_top_role.position}) ≤ Cargo ({cargo.position})")
            print(f"💡 Solução: Arraste o cargo do bot ACIMA do cargo {cargo.name}")
            return
        
        # Dar o cargo
        await member.add_roles(cargo, reason="Auto-role: entrada no servidor")
        print(f"✅ Cargo '{cargo.name}' dado para {member.name}")
        
        # Log no console
        print(f"📝 {member.name} recebeu o cargo {cargo.name}")
        
    except discord.Forbidden:
        print("❌ PERMISSÃO NEGADA: Bot não pode dar este cargo")
    except Exception as e:
        print(f"❌ ERRO: {type(e).__name__}: {e}")

# ========== COMANDOS DE TESTE ==========
@bot.command()
async def test_autorole(ctx, member: discord.Member = None):
    """Testa o sistema de auto-role"""
    if member is None:
        member = ctx.author
    
    cargo = ctx.guild.get_role(CARGO_ID)
    
    if not cargo:
        await ctx.send(f"❌ Cargo com ID `{CARGO_ID}` não encontrado!")
        return
    
    try:
        await member.add_roles(cargo)
        await ctx.send(f"✅ Teste OK! Cargo {cargo.mention} dado para {member.mention}")
    except Exception as e:
        await ctx.send(f"❌ Erro: `{type(e).__name__}: {e}`")

@bot.command()
async def autorole_info(ctx):
    """Mostra informações do sistema de auto-role"""
    cargo = ctx.guild.get_role(CARGO_ID)
    
    embed = discord.Embed(
        title="🛬 Sistema de Auto-Role",
        color=discord.Color.blue()
    )
    
    if cargo:
        embed.description = f"**Cargo alvo:** {cargo.mention} (`{cargo.id}`)"
        embed.add_field(name="🎨 Cor", value=str(cargo.color), inline=True)
        embed.add_field(name="👥 Membros", value=len(cargo.members), inline=True)
        embed.add_field(name="📊 Posição", value=f"#{cargo.position}", inline=True)
        
        # Verificar permissões
        bot_member = ctx.guild.get_member(bot.user.id)
        if bot_member.guild_permissions.manage_roles:
            embed.add_field(name="✅ Permissão", value="Gerenciar Cargos", inline=True)
        else:
            embed.add_field(name="❌ Permissão", value="Falta: Gerenciar Cargos", inline=True)
        
        # Verificar hierarquia
        bot_top_role = bot_member.top_role
        if bot_top_role.position > cargo.position:
            embed.add_field(name="✅ Hierarquia", value="Bot acima do cargo", inline=True)
        else:
            embed.add_field(name="❌ Hierarquia", value="Bot abaixo do cargo", inline=True)
            
        embed.set_footer(text="Status: Ativo ✅")
    else:
        embed.description = f"❌ Cargo com ID `{CARGO_ID}` não encontrado!"
        embed.add_field(
            name="🆔 Como encontrar o ID:",
            value="1. Ative Modo Desenvolvedor\n2. Clique direito no cargo → Copiar ID",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def set_cargo_id(ctx, novo_id: int):
    """Define um novo ID de cargo para auto-role"""
    global CARGO_ID
    CARGO_ID = novo_id
    
    cargo = ctx.guild.get_role(CARGO_ID)
    if cargo:
        await ctx.send(f"✅ Auto-role configurado para: {cargo.mention} (`{cargo.id}`)")
    else:
        await ctx.send(f"⚠️ ID `{novo_id}` definido, mas cargo não encontrado")

# ========== INICIAR BOT ==========
if __name__ == "__main__":
    # Lê o token da variável de ambiente
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("💡 Configure a variável de ambiente ou coloque o token diretamente")
        exit(1)
    
    print("🚀 Iniciando bot...")
    bot.run(TOKEN)
