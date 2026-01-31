import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
from datetime import datetime
import re

# ========== CONFIGURAÇÃO ==========
# Dicionário de cargos com prefixos de nickname
NICKNAME_CONFIG = {
    "00": "00 | {nick}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞": "GER | {nick} - {id}",
    "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫": "SLD | {nick} - {id}",
    "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫": "REC | {nick} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞": "GER ELITE | {nick} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨": "GER REC | {nick} - {id}",
  "𝐄𝐥𝐢𝐭𝐞": "ELITE | {nick} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫": "GER FMR | {nick}",
    "𝐌𝐨𝐝𝐞𝐫": "MOD | {nick}",
    "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨": "AV | {nick} - {id}",
    "𝐌𝐞𝐦𝐛𝐫𝐨": "MEM | {nick}",
    "𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞": "{nick}",
    "𝐀𝐃𝐌": "ADM | {nick} - {id}",  # Adicionado cargo ADM
}

# Ordem de prioridade (do mais importante para o menos)
ORDEM_PRIORIDADE = [
    "00",
    "𝐀𝐃𝐌",
    "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", 
    "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞",
  "𝐄𝐥𝐢𝐭𝐞"
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫",
    "𝐌𝐨𝐝𝐞𝐫",
    "𝐌𝐞𝐦𝐛𝐫𝐨",
    "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨",
    "𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞"
]

# Cargos que podem usar o sistema
STAFF_ROLES = [
    "00", 
    "𝐀𝐃𝐌",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", 
    "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", 
    "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", 
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", 
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", 
    "𝐌𝐨𝐝𝐞𝐫"
]

# ========== BANCO DE DADOS SIMPLES (MEMÓRIA) ==========
# Armazena associação entre ID do Discord e ID do FiveM
fivem_database = {}  # Formato: {discord_id: fivem_id}

class FivemIDModal(ui.Modal, title="🔢 Configurar ID do FiveM"):
    """Modal para configurar ID do FiveM"""
    
    fivem_id = ui.TextInput(
        label="Digite seu ID do FiveM:",
        placeholder="Ex: 76561198012345678",
        style=discord.TextStyle.short,
        required=True,
        min_length=6,
        max_length=20
    )
    
    def __init__(self, member: discord.Member):
        super().__init__()
        self.member = member
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Validar se é um número
        if not self.fivem_id.value.isdigit():
            await interaction.followup.send("❌ ID do FiveM deve conter apenas números!", ephemeral=True)
            return
        
        # Salvar no banco de dados
        fivem_database[str(self.member.id)] = self.fivem_id.value
        
        # Atualizar nickname
        success = await atualizar_nickname_com_cargo(self.member)
        
        if success:
            embed = discord.Embed(
                title="✅ ID do FiveM Configurado",
                description=f"**ID do FiveM:** `{self.fivem_id.value}`\n**Discord:** {self.member.mention}",
                color=discord.Color.green()
            )
            embed.set_footer(text="Nickname atualizado automaticamente")
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("✅ ID do FiveM salvo, mas não foi possível atualizar o nickname.", ephemeral=True)

# ========== FUNÇÕES AUXILIARES ==========
def extrair_fivem_id_do_nickname(nickname: str) -> str:
    """Extrai ID do FiveM do nickname atual"""
    if not nickname:
        return "???"
    
    # Tentar padrão: "PREFIXO | Nome - ID"
    match = re.search(r' - (\d+)$', nickname)
    if match:
        return match.group(1)
    
    # Tentar padrão com hífen diferente
    match = re.search(r'-(\d+)$', nickname)
    if match:
        return match.group(1)
    
    # Tentar padrão: qualquer número no final
    match = re.search(r'(\d{4,})$', nickname)
    if match:
        return match.group(1)
    
    return "???"

async def atualizar_nickname_com_cargo(member: discord.Member) -> bool:
    """Atualiza o nickname baseado no cargo mais importante e ID do FiveM"""
    try:
        # Verificar permissões do bot
        if not member.guild.me.guild_permissions.manage_nicknames:
            print(f"❌ Bot não tem permissão para gerenciar nicknames")
            return False
        
        # Encontrar cargo mais importante que o membro tem
        cargo_principal = None
        for cargo_nome in ORDEM_PRIORIDADE:
            cargo_obj = discord.utils.get(member.roles, name=cargo_nome)
            if cargo_obj:
                cargo_principal = cargo_nome
                break
        
        if not cargo_principal:
            print(f"ℹ️ {member.name} não tem cargo configurado")
            return False
        
        if cargo_principal not in NICKNAME_CONFIG:
            print(f"⚠️ Cargo {cargo_principal} não tem template configurado")
            return False
        
        # Obter ID do FiveM
        fivem_id = "???"
        
        # 1. Tentar do banco de dados
        if str(member.id) in fivem_database:
            fivem_id = fivem_database[str(member.id)]
        
        # 2. Se não encontrar, tentar extrair do nickname atual
        if fivem_id == "???" and member.nick:
            extracted_id = extrair_fivem_id_do_nickname(member.nick)
            if extracted_id != "???":
                fivem_id = extracted_id
                # Salvar no banco de dados para futuras referências
                fivem_database[str(member.id)] = fivem_id
        
        # 3. Se ainda não encontrar, usar o nome do usuário
        if fivem_id == "???":
            # Tentar extrair números do nome
            match = re.search(r'(\d{4,})', member.name)
            if match:
                fivem_id = match.group(1)
                fivem_database[str(member.id)] = fivem_id
        
        # Gerar novo nickname
        # Usar o primeiro nome (antes de espaço) ou nome completo se não houver espaço
        nome_base = member.name.split()[0] if ' ' in member.name else member.name
        nome_base = nome_base[:15]  # Limitar tamanho
        
        template = NICKNAME_CONFIG[cargo_principal]
        novo_nick = template.format(nick=nome_base, id=fivem_id)
        
        # Garantir que não ultrapasse 32 caracteres (limite do Discord)
        if len(novo_nick) > 32:
            # Se ainda estiver muito grande, reduzir o nome base
            excesso = len(novo_nick) - 32
            nome_base = nome_base[:-excesso] if len(nome_base) > excesso else nome_base[:3]
            novo_nick = template.format(nick=nome_base, id=fivem_id)
            
            # Se ainda estiver grande, truncar
            if len(novo_nick) > 32:
                novo_nick = novo_nick[:32]
        
        # Verificar se o nickname já está correto
        if member.nick == novo_nick:
            print(f"ℹ️ Nickname já está atualizado: {member.name}")
            return True
        
        # Aplicar nickname
        try:
            await member.edit(nick=novo_nick)
            print(f"✅ Nickname atualizado para {member.name}: {novo_nick}")
            return True
        except discord.HTTPException as e:
            print(f"❌ Erro HTTP ao editar nickname: {e}")
            return False
            
    except discord.Forbidden:
        print(f"❌ Sem permissão para alterar nickname de {member.name}")
        return False
    except Exception as e:
        print(f"❌ Erro ao atualizar nickname: {type(e).__name__}: {e}")
        return False

async def atualizar_nickname_apos_cargo(member: discord.Member):
    """Função auxiliar para atualizar nickname após mudança de cargo"""
    await asyncio.sleep(1)  # Pequena espera para garantir que o cargo foi aplicado
    await atualizar_nickname_com_cargo(member)

# ========== CLASSES DO SISTEMA ==========
class CargoSelectView(ui.View):
    """View com dropdown para selecionar cargo"""
    def __init__(self, target_member, action="add"):
        super().__init__(timeout=60)
        self.target_member = target_member
        self.action = action
        self.add_item(CargoSelectDropdown(target_member, action))

class CargoSelectDropdown(ui.Select):
    def __init__(self, target_member, action="add"):
        self.target_member = target_member
        self.action = action
        
        options = [
            discord.SelectOption(label="00", description="Dono", emoji="👑"),
            discord.SelectOption(label="𝐀𝐃𝐌", description="Administrador", emoji="🛡️"),
            discord.SelectOption(label="𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞", description="𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞", emoji="🌟"),
            discord.SelectOption(label="𝐆𝐞𝐫𝐞𝐧𝐭𝐞", description="𝐆𝐞𝐫𝐞𝐧𝐭𝐞", emoji="⚙️"),
            discord.SelectOption(label="𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", description="𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", emoji="🔧"),
            discord.SelectOption(label="𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", description="𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", emoji="📋"),
            discord.SelectOption(label="𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", description="𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", emoji="❤️"),
            discord.SelectOption(label="𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", description="𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", emoji="📈"),
            discord.SelectOption(label="𝐌𝐨𝐝𝐞𝐫", description="𝐌𝐨𝐝𝐞𝐫", emoji="🛡️"),
            discord.SelectOption(label="𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨", description="Cargo inicial", emoji="✈️"),
            discord.SelectOption(label="𝐌𝐞𝐦𝐛𝐫𝐨", description="Membro do servidor", emoji="👤"),
            discord.SelectOption(label="𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞", description="𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞", emoji="👋"),
        ]
        
        super().__init__(
            placeholder="Selecione um cargo...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="cargo_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        if not any(role.name in STAFF_ROLES for role in interaction.user.roles):
            await interaction.followup.send("❌ Apenas staff pode gerenciar cargos!", ephemeral=True)
            return
        
        cargo_nome = self.values[0]
        cargo = discord.utils.get(interaction.guild.roles, name=cargo_nome)
        
        if not cargo:
            await interaction.followup.send(f"❌ Cargo `{cargo_nome}` não encontrado!", ephemeral=True)
            return
        
        try:
            if self.action == "add":
                if cargo in self.target_member.roles:
                    await interaction.followup.send(f"❌ {self.target_member.mention} já possui o cargo `{cargo.name}`!", ephemeral=True)
                    return
                
                await self.target_member.add_roles(cargo)
                mensagem = f"✅ Cargo `{cargo.name}` adicionado para {self.target_member.mention}!"
                cor = discord.Color.green()
                
            else:  # remove
                if cargo not in self.target_member.roles:
                    await interaction.followup.send(f"❌ {self.target_member.mention} não possui o cargo `{cargo.name}`!", ephemeral=True)
                    return
                
                await self.target_member.remove_roles(cargo)
                mensagem = f"✅ Cargo `{cargo.name}` removido de {self.target_member.mention}!"
                cor = discord.Color.orange()
            
            # Atualizar nickname após mudança de cargo
            bot.loop.create_task(atualizar_nickname_apos_cargo(self.target_member))
            
            embed = discord.Embed(
                title=f"⚙️ Cargo {'Adicionado' if self.action == 'add' else 'Removido'}",
                description=mensagem,
                color=cor
            )
            embed.add_field(name="👤 Usuário", value=self.target_member.mention, inline=True)
            embed.add_field(name="🎯 Cargo", value=cargo.mention, inline=True)
            embed.add_field(name="👑 Staff", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
            await interaction.channel.send(embed=embed)
            await interaction.followup.send(f"✅ Operação realizada! Nickname será atualizado.", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ Não tenho permissão para gerenciar cargos!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

class CargoPanelView(ui.View):
    """View principal do painel de cargos"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="➕ Adicionar Cargo", style=ButtonStyle.green, emoji="➕", custom_id="add_cargo")
    async def add_cargo(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.name in STAFF_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode adicionar cargos!", ephemeral=True)
            return
        
        modal = AddCargoModal()
        await interaction.response.send_modal(modal)
    
    @ui.button(label="➖ Remover Cargo", style=ButtonStyle.red, emoji="➖", custom_id="remove_cargo")
    async def remove_cargo(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.name in STAFF_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode remover cargos!", ephemeral=True)
            return
        
        modal = RemoveCargoModal()
        await interaction.response.send_modal(modal)
    
    @ui.button(label="📋 Ver Cargos", style=ButtonStyle.blurple, emoji="📋", custom_id="view_cargos")
    async def view_cargos(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.name in STAFF_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode ver cargos!", ephemeral=True)
            return
        
        modal = ViewCargosModal()
        await interaction.response.send_modal(modal)
    
    @ui.button(label="🔢 Configurar ID", style=ButtonStyle.gray, emoji="🔢", custom_id="set_fivem_id")
    async def set_fivem_id(self, interaction: discord.Interaction, button: ui.Button):
        """Configura o ID do FiveM"""
        modal = FivemIDModal(interaction.user)
        await interaction.response.send_modal(modal)

class AddCargoModal(ui.Modal, title="➕ Adicionar Cargo"):
    usuario = ui.TextInput(
        label="Nome, ID Discord ou ID FiveM:",
        placeholder="Ex: @usuario, 123456 ou FiveM ID",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            member = None
            
            # Primeiro, tentar encontrar por ID do FiveM no banco de dados
            fivem_id = None
            if self.usuario.value.isdigit() and len(self.usuario.value) >= 6:
                # Pode ser ID do FiveM
                for discord_id, stored_fivem_id in fivem_database.items():
                    if stored_fivem_id == self.usuario.value:
                        member = interaction.guild.get_member(int(discord_id))
                        fivem_id = stored_fivem_id
                        break
            
            # Se não encontrou por FiveM ID, tentar métodos normais
            if not member:
                if "<@" in self.usuario.value:  # Menção
                    user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                    member = interaction.guild.get_member(int(user_id))
                elif self.usuario.value.isdigit() and len(self.usuario.value) <= 20:  # Discord ID
                    member = interaction.guild.get_member(int(self.usuario.value))
                else:  # Nome
                    for guild_member in interaction.guild.members:
                        if self.usuario.value.lower() in guild_member.name.lower():
                            member = guild_member
                            break
            
            if not member:
                await interaction.followup.send(f"❌ Usuário `{self.usuario.value}` não encontrado!", ephemeral=True)
                return
            
            # Verificar se tem ID do FiveM configurado
            if str(member.id) not in fivem_database:
                embed = discord.Embed(
                    title="⚠️ Aviso - ID do FiveM",
                    description=(
                        f"{member.mention} não tem ID do FiveM configurado!\n\n"
                        f"**Para configurar:**\n"
                        f"1. Clique em '🔢 Configurar ID' no painel\n"
                        f"2. Digite o ID do FiveM\n"
                        f"3. O nickname será formatado automaticamente\n\n"
                        f"📌 **ID do FiveM encontrado em:**\n"
                        f"• FiveM → Settings → Profile → Copy Identifier"
                    ),
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            
            view = CargoSelectView(member, action="add")
            embed = discord.Embed(
                title="🎯 Selecione o Cargo",
                description=(
                    f"**Usuário:** {member.mention}\n"
                    f"**ID Discord:** `{member.id}`\n"
                    f"**ID FiveM:** `{fivem_database.get(str(member.id), 'Não configurado')}`\n"
                    f"**Ação:** **Adicionar Cargo**"
                ),
                color=discord.Color.blue()
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

class RemoveCargoModal(ui.Modal, title="➖ Remover Cargo"):
    usuario = ui.TextInput(
        label="Nome, ID Discord ou ID FiveM:",
        placeholder="Ex: @usuario, 123456 ou FiveM ID",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            member = None
            
            # Primeiro, tentar encontrar por ID do FiveM
            fivem_id = None
            if self.usuario.value.isdigit() and len(self.usuario.value) >= 6:
                for discord_id, stored_fivem_id in fivem_database.items():
                    if stored_fivem_id == self.usuario.value:
                        member = interaction.guild.get_member(int(discord_id))
                        fivem_id = stored_fivem_id
                        break
            
            # Se não encontrou por FiveM ID, tentar métodos normais
            if not member:
                if "<@" in self.usuario.value:
                    user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                    member = interaction.guild.get_member(int(user_id))
                elif self.usuario.value.isdigit() and len(self.usuario.value) <= 20:
                    member = interaction.guild.get_member(int(self.usuario.value))
                else:
                    for guild_member in interaction.guild.members:
                        if self.usuario.value.lower() in guild_member.name.lower():
                            member = guild_member
                            break
            
            if not member:
                await interaction.followup.send(f"❌ Usuário `{self.usuario.value}` não encontrado!", ephemeral=True)
                return
            
            view = CargoSelectView(member, action="remove")
            embed = discord.Embed(
                title="🎯 Selecione o Cargo",
                description=(
                    f"**Usuário:** {member.mention}\n"
                    f"**ID Discord:** `{member.id}`\n"
                    f"**ID FiveM:** `{fivem_database.get(str(member.id), 'Não configurado')}`\n"
                    f"**Ação:** **Remover Cargo**"
                ),
                color=discord.Color.orange()
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

class ViewCargosModal(ui.Modal, title="📋 Ver Cargos do Usuário"):
    usuario = ui.TextInput(
        label="Nome, ID Discord ou ID FiveM:",
        placeholder="Ex: @usuario, 123456 ou FiveM ID",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            member = None
            encontrado_por = "Discord"
            
            # Primeiro, tentar encontrar por ID do FiveM
            if self.usuario.value.isdigit() and len(self.usuario.value) >= 6:
                for discord_id, stored_fivem_id in fivem_database.items():
                    if stored_fivem_id == self.usuario.value:
                        member = interaction.guild.get_member(int(discord_id))
                        encontrado_por = f"FiveM ID: {stored_fivem_id}"
                        break
            
            # Se não encontrou por FiveM ID, tentar métodos normais
            if not member:
                if "<@" in self.usuario.value:
                    user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                    member = interaction.guild.get_member(int(user_id))
                    encontrado_por = "Menção Discord"
                elif self.usuario.value.isdigit() and len(self.usuario.value) <= 20:
                    member = interaction.guild.get_member(int(self.usuario.value))
                    encontrado_por = "ID Discord"
                else:
                    for guild_member in interaction.guild.members:
                        if self.usuario.value.lower() in guild_member.name.lower():
                            member = guild_member
                            encontrado_por = "Nome"
                            break
            
            if not member:
                await interaction.followup.send(f"❌ Usuário `{self.usuario.value}` não encontrado!", ephemeral=True)
                return
            
            cargos = [role.mention for role in member.roles if role.name != "@everyone"]
            
            embed = discord.Embed(
                title=f"📋 Informações de {member.name}",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            
            # Informações básicas
            embed.add_field(name="🆔 ID Discord", value=f"`{member.id}`", inline=True)
            embed.add_field(name="🔢 ID FiveM", value=f"`{fivem_database.get(str(member.id), 'Não configurado')}`", inline=True)
            embed.add_field(name="🔍 Encontrado por", value=encontrado_por, inline=True)
            
            # Cargos
            if cargos:
                embed.add_field(
                    name=f"🎯 Cargos ({len(cargos)})",
                    value="\n".join(cargos[:10]),
                    inline=False
                )
                if len(cargos) > 10:
                    embed.add_field(name="...", value=f"*+ {len(cargos)-10} cargos*", inline=False)
            else:
                embed.add_field(name="🎯 Cargos", value="Apenas @everyone", inline=False)
            
            # Nickname atual
            embed.add_field(name="🎮 Nickname Atual", value=f"`{member.nick or member.name}`", inline=True)
            
            # Cargo principal para nickname
            cargo_principal = None
            for cargo_nome in ORDEM_PRIORIDADE:
                if discord.utils.get(member.roles, name=cargo_nome):
                    cargo_principal = cargo_nome
                    break
            
            if cargo_principal:
                template = NICKNAME_CONFIG.get(cargo_principal, "{nick}")
                fivem_id = fivem_database.get(str(member.id), "??")
                nome_base = member.name.split()[0] if ' ' in member.name else member.name
                nome_base = nome_base[:15]
                nickname_calculado = template.format(nick=nome_base, id=fivem_id)
                embed.add_field(name="📝 Nickname Calculado", value=f"`{nickname_calculado}`", inline=True)
            
            # Informações adicionais
            if member.joined_at:
                embed.add_field(name="📅 Entrou em", value=member.joined_at.strftime('%d/%m/%Y'), inline=True)
            embed.add_field(name="👤 Conta criada", value=member.created_at.strftime('%d/%m/%Y'), inline=True)
            
            embed.set_footer(text=f"Solicitado por: {interaction.user.name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

# ========== COG PRINCIPAL ==========
class CargosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ Módulo de Cargos carregado!")
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Monitora mudanças de cargo para atualizar nickname"""
        if before.roles != after.roles:
            print(f"🔄 Cargos alterados para {after.name}")
            await asyncio.sleep(1)  # Pequeno delay
            await atualizar_nickname_com_cargo(after)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Quando o bot inicia, carrega views persistentes"""
        # Adiciona a view persistente
        self.bot.add_view(CargoPanelView())
        print("✅ Views de cargos carregadas persistentemente")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_cargos(self, ctx):
        """Configura o painel de gerenciamento de cargos"""
        
        embed = discord.Embed(
            title="⚙️ **PAINEL DE GERENCIAMENTO DE CARGOS**",
            description=(
                "**Funcionalidades disponíveis:**\n\n"
                "➕ **Adicionar Cargo** - Adiciona um cargo a um usuário\n"
                "➖ **Remover Cargo** - Remove um cargo de um usuário\n"
                "📋 **Ver Cargos** - Mostra informações do usuário\n"
                "🔢 **Configurar ID** - Configura ID do FiveM\n\n"
                "**📌 Como usar:**\n"
                "1. Clique em uma das opções acima\n"
                "2. Digite nome/ID do Discord ou ID do FiveM\n"
                "3. Selecione o cargo desejado\n"
                "✅ Nickname atualizado automaticamente com ID do FiveM!"
            ),
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Sistema Automático de Nickname",
            value=(
                "• **00** → 00 | Nome\n"
                "• **𝐀𝐃𝐌** → ADM | Nome - ID\n"
                "• **𝐆𝐞𝐫𝐞𝐧𝐭𝐞** → GER | Nome - ID\n"
                "• **𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫** → SLD | Nome - ID\n"
                "• **𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫** → REC | Nome - ID\n"
                "• **𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞** → GER ELITE | Nome - ID\n"
                "• **𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨** → GER REC | Nome - ID\n"
                "• **𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨** → AV | Nome - ID\n"
                "\n**📌 ID do FiveM:**\n"
                "FiveM → Settings → Profile → Copy Identifier"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Apenas Staff",
            value="\n".join([f"• {role}" for role in STAFF_ROLES]),
            inline=False
        )
        
        embed.add_field(
            name="🔍 Buscar por:",
            value="• Menção (@usuario)\n• ID do Discord\n• ID do FiveM\n• Nome do usuário",
            inline=False
        )
        
        embed.set_footer(text="Sistema automático de cargos • Hospício APP")
        
        view = CargoPanelView()
        
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()
    
    @commands.command()
    async def atualizar_nick(self, ctx, member: discord.Member = None):
        """Atualiza manualmente o nickname baseado nos cargos"""
        if member is None:
            member = ctx.author
        
        # Verificar se é staff ou o próprio usuário
        is_staff = any(role.name in STAFF_ROLES for role in ctx.author.roles)
        if not is_staff and ctx.author.id != member.id:
            await ctx.send("❌ Você só pode atualizar seu próprio nickname!")
            return
        
        # Verificar se tem ID do FiveM configurado
        if str(member.id) not in fivem_database:
            embed = discord.Embed(
                title="⚠️ Configure seu ID do FiveM",
                description=(
                    f"{member.mention}, você precisa configurar seu ID do FiveM primeiro!\n\n"
                    f"**Como configurar:**\n"
                    f"1. No painel de cargos, clique em '🔢 Configurar ID'\n"
                    f"2. Digite seu ID do FiveM\n"
                    f"3. O sistema formatará seu nickname automaticamente\n\n"
                    f"**📍 Onde encontrar o ID do FiveM:**\n"
                    f"FiveM → Settings → Profile → Copy Identifier"
                ),
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        success = await atualizar_nickname_com_cargo(member)
        
        if success:
            await ctx.send(f"✅ Nickname de {member.mention} atualizado para `{member.nick}`")
        else:
            await ctx.send(f"❌ Não foi possível atualizar o nickname de {member.mention}")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_fivem(self, ctx, member: discord.Member, fivem_id: str):
        """Configura o ID do FiveM para um membro (apenas ADM)"""
        if not fivem_id.isdigit():
            await ctx.send("❌ ID do FiveM deve conter apenas números!")
            return
        
        fivem_database[str(member.id)] = fivem_id
        
        # Atualizar nickname
        success = await atualizar_nickname_com_cargo(member)
        
        embed = discord.Embed(
            title="✅ ID do FiveM Configurado",
            description=(
                f"**Usuário:** {member.mention}\n"
                f"**ID Discord:** `{member.id}`\n"
                f"**ID FiveM:** `{fivem_id}`\n"
                f"**Nickname atualizado:** {'✅ Sim' if success else '❌ Não'}"
            ),
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def list_fivem_ids(self, ctx):
        """Lista todos os IDs do FiveM configurados (apenas ADM)"""
        if not fivem_database:
            await ctx.send("📭 Nenhum ID do FiveM configurado ainda.")
            return
        
        embed = discord.Embed(
            title="📋 IDs do FiveM Configurados",
            description=f"Total: {len(fivem_database)} usuários",
            color=discord.Color.blue()
        )
        
        # Agrupar por páginas se muitos registros
        items = list(fivem_database.items())
        for i in range(0, len(items), 10):
            page_items = items[i:i+10]
            field_value = ""
            
            for discord_id, fivem_id in page_items:
                member = ctx.guild.get_member(int(discord_id))
                member_name = member.mention if member else f"ID: {discord_id}"
                field_value += f"{member_name} → `{fivem_id}`\n"
            
            embed.add_field(
                name=f"Página {i//10 + 1}",
                value=field_value or "Nenhum",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def meu_id(self, ctx):
        """Mostra seu ID do FiveM configurado"""
        fivem_id = fivem_database.get(str(ctx.author.id))
        
        if fivem_id:
            embed = discord.Embed(
                title="🔢 Seu ID do FiveM",
                description=f"**ID FiveM:** `{fivem_id}`\n**Discord:** {ctx.author.mention}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="⚠️ ID do FiveM não configurado",
                description=(
                    f"{ctx.author.mention}, você ainda não configurou seu ID do FiveM!\n\n"
                    f"**Para configurar:**\n"
                    f"1. No painel de cargos, clique em '🔢 Configurar ID'\n"
                    f"2. Digite seu ID do FiveM\n"
                    f"3. O sistema formatará seu nickname automaticamente\n\n"
                    f"**📍 Onde encontrar:**\n"
                    f"FiveM → Settings → Profile → Copy Identifier"
                ),
                color=discord.Color.orange()
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CargosCog(bot))
    print("✅ Sistema de Cargos configurado!")
