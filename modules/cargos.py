import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
from datetime import datetime

# ========== CONFIGURAÇÃO ==========
NICKNAME_CONFIG = {
    "00": "00 | {nick}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞": "GER | {nick} - {id}",
    "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫": "SLD | {nick} - {id}",
    "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫": "REC | {nick} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞": "GER ELITE | {nick} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨": "GER REC | {nick} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫": "GER FMR | {nick}",
    "𝐌𝐨𝐝𝐞𝐫": "MOD | {nick}",
    "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨": "AV | {nick} - {id}",
    "𝐌𝐞𝐦𝐛𝐫𝐨": "MBR | {nick}",
    "𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞": "{nick}",
}

STAFF_ROLES = [
    "00", 
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", 
    "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", 
    "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", 
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", 
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", 
    "𝐌𝐨𝐝𝐞𝐫"
]

# ========== FUNÇÕES AUXILIARES ==========
async def atualizar_nickname_com_cargo(member: discord.Member):
    """Atualiza o nickname baseado no cargo mais importante"""
    try:
        # Ordem de prioridade dos cargos
        ordem_prioridade = [
            "00",
            "𝐆𝐞𝐫𝐞𝐧𝐭𝐞",
            "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", 
            "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫",
            "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞",
            "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨",
            "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫",
            "𝐌𝐨𝐝𝐞𝐫",
            "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨",
            "𝐌𝐞𝐦𝐛𝐫𝐨",
            "𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞"
        ]
        
        # Encontrar cargo mais importante que o membro tem
        cargo_principal = None
        for cargo_nome in ordem_prioridade:
            cargo_obj = discord.utils.get(member.roles, name=cargo_nome)
            if cargo_obj:
                cargo_principal = cargo_nome
                break
        
        if cargo_principal and cargo_principal in NICKNAME_CONFIG:
            # Extrair ID do FiveM do nickname atual (se existir)
            fivem_id = "???"
            if member.nick:
                import re
                match = re.search(r'- (\d+)$', member.nick)
                if match:
                    fivem_id = match.group(1)
            elif member.name:
                # Tentar extrair do nome
                match = re.search(r'(\d{4,})$', member.name)
                if match:
                    fivem_id = match.group(1)
            
            # Gerar novo nickname
            nick_base = member.name.split()[0] if ' ' in member.name else member.name
            template = NICKNAME_CONFIG[cargo_principal]
            novo_nick = template.format(nick=nick_base[:15], id=fivem_id)
            
            # Garantir que não ultrapasse 32 caracteres
            if len(novo_nick) > 32:
                novo_nick = novo_nick[:32]
            
            # Aplicar nickname
            await member.edit(nick=novo_nick)
            print(f"✅ Nickname atualizado para {member.name}: {novo_nick}")
            return True
    except discord.Forbidden:
        print(f"❌ Sem permissão para alterar nickname de {member.name}")
    except Exception as e:
        print(f"❌ Erro ao atualizar nickname: {e}")
    
    return False

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
                
                # Atualizar nickname
                await atualizar_nickname_com_cargo(self.target_member)
                
            else:  # remove
                if cargo not in self.target_member.roles:
                    await interaction.followup.send(f"❌ {self.target_member.mention} não possui o cargo `{cargo.name}`!", ephemeral=True)
                    return
                
                await self.target_member.remove_roles(cargo)
                mensagem = f"✅ Cargo `{cargo.name}` removido de {self.target_member.mention}!"
                cor = discord.Color.orange()
                
                # Recalcular nickname
                await atualizar_nickname_com_cargo(self.target_member)
            
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
            await interaction.followup.send(f"✅ Operação realizada! Nickname atualizado.", ephemeral=True)
            
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

class AddCargoModal(ui.Modal, title="➕ Adicionar Cargo"):
    usuario = ui.TextInput(
        label="Nome ou ID do usuário:",
        placeholder="Ex: @usuario ou 123456789012345678",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            member = None
            
            if "<@" in self.usuario.value:
                user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                member = interaction.guild.get_member(int(user_id))
            elif self.usuario.value.isdigit():
                member = interaction.guild.get_member(int(self.usuario.value))
            else:
                for guild_member in interaction.guild.members:
                    if self.usuario.value.lower() in guild_member.name.lower():
                        member = guild_member
                        break
            
            if not member:
                await interaction.followup.send(f"❌ Usuário `{self.usuario.value}` não encontrado!", ephemeral=True)
                return
            
            view = CargoSelectView(member, action="add")
            embed = discord.Embed(
                title="🎯 Selecione o Cargo",
                description=f"Usuário: {member.mention}\nAção: **Adicionar Cargo**",
                color=discord.Color.blue()
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

class RemoveCargoModal(ui.Modal, title="➖ Remover Cargo"):
    usuario = ui.TextInput(
        label="Nome ou ID do usuário:",
        placeholder="Ex: @usuario ou 123456789012345678",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            member = None
            
            if "<@" in self.usuario.value:
                user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                member = interaction.guild.get_member(int(user_id))
            elif self.usuario.value.isdigit():
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
                description=f"Usuário: {member.mention}\nAção: **Remover Cargo**",
                color=discord.Color.orange()
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

class ViewCargosModal(ui.Modal, title="📋 Ver Cargos do Usuário"):
    usuario = ui.TextInput(
        label="Nome ou ID do usuário:",
        placeholder="Ex: @usuario ou 123456789012345678",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            member = None
            
            if "<@" in self.usuario.value:
                user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                member = interaction.guild.get_member(int(user_id))
            elif self.usuario.value.isdigit():
                member = interaction.guild.get_member(int(self.usuario.value))
            else:
                for guild_member in interaction.guild.members:
                    if self.usuario.value.lower() in guild_member.name.lower():
                        member = guild_member
                        break
            
            if not member:
                await interaction.followup.send(f"❌ Usuário `{self.usuario.value}` não encontrado!", ephemeral=True)
                return
            
            cargos = [role.mention for role in member.roles if role.name != "@everyone"]
            
            embed = discord.Embed(
                title=f"📋 Cargos de {member.name}",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            
            if cargos:
                embed.description = "\n".join(cargos)
                embed.add_field(name="Total de Cargos", value=str(len(cargos)), inline=True)
            else:
                embed.description = "Nenhum cargo além do @everyone"
            
            embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
            embed.add_field(name="📅 Entrou em", value=member.joined_at.strftime('%d/%m/%Y') if member.joined_at else "N/A", inline=True)
            embed.add_field(name="🎮 Nickname", value=f"`{member.nick or member.name}`", inline=False)
            embed.set_footer(text=f"Solicitado por: {interaction.user.name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

# ========== COG PRINCIPAL ==========
class CargosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ Módulo de Cargos carregado!")
    
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
                "📋 **Ver Cargos** - Mostra todos os cargos de um usuário\n\n"
                "**📌 Como usar:**\n"
                "1. Clique em uma das opções acima\n"
                "2. Digite o nome/ID do usuário\n"
                "3. Selecione o cargo desejado\n"
                "✅ Nickname atualizado automaticamente!"
            ),
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Sistema Automático de Nickname",
            value=(
                "• **00** → 00 | Nome\n"
                "• **𝐆𝐞𝐫𝐞𝐧𝐭𝐞** → GER | Nome - ID\n"
                "• **𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫** → SLD | Nome - ID\n"
                "• **𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫** → REC | Nome - ID\n"
                "• **𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞** → GER ELITE | Nome - ID\n"
                "• **𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨** → GER REC | Nome - ID\n"
                "• **𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨** → AV | Nome - ID"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Apenas Staff",
            value="\n".join([f"• {role}" for role in STAFF_ROLES]),
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
        
        success = await atualizar_nickname_com_cargo(member)
        
        if success:
            await ctx.send(f"✅ Nickname de {member.mention} atualizado para `{member.nick}`")
        else:
            await ctx.send(f"❌ Não foi possível atualizar o nickname de {member.mention}")

async def setup(bot):
    await bot.add_cog(CargosCog(bot))
    print("✅ Sistema de Cargos configurado!")
