import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
from datetime import datetime
import re

# ========== CONFIGURAÇÃO SIMPLES ==========
NICKNAME_CONFIG = {
    "00": "00 | {name}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞": "GER | {name} - {id}",
    "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫": "SLD | {name} - {id}",
    "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫": "REC | {name} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞": "GER ELITE | {name} - {id}",
    "𝐄𝐥𝐢𝐭𝐞": "ELITE | {nick} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨": "GER REC | {name} - {id}",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫": "GER FMR | {name}",
    "𝐌𝐨𝐝𝐞𝐫": "MOD | {name}",
    "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨": "AV | {name} - {id}",
    "𝐌𝐞𝐦𝐛𝐫𝐨": "MEM | {name} - {id}",
    "𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞": "{name}",
    "𝐀𝐃𝐌": "ADM | {name} - {id}",
}

ORDEM_PRIORIDADE = [
    "00", "𝐀𝐃𝐌", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞", "𝐄𝐥𝐢𝐭𝐞", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨",
    "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "𝐌𝐨𝐝𝐞𝐫", "𝐌𝐞𝐦𝐛𝐫𝐨",
    "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨", "𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞"
]

STAFF_ROLES = ["00", "𝐀𝐃𝐌", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", 
               "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", 
               "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "𝐌𝐨𝐝𝐞𝐫"]

# ========== FUNÇÕES SIMPLES ==========
def extrair_parte_nickname(nickname: str):
    """Extrai a primeira parte do nickname (antes do ' - ')"""
    if not nickname:
        return "User"
    
    # Padrão: "PREFIX | Nome - ID" ou apenas "Nome - ID"
    parts = nickname.split(' - ')
    if len(parts) > 1:
        primeira_parte = parts[0]
        # Remover prefixo se existir (ex: "MEM | ")
        if ' | ' in primeira_parte:
            primeira_parte = primeira_parte.split(' | ')[1]
        return primeira_parte.strip()
    
    # Se não tem traço, pode ser apenas o nome
    if ' | ' in nickname:
        return nickname.split(' | ')[1].strip()
    
    return nickname.strip()

def extrair_id_fivem(nickname: str):
    """Extrai ID do FiveM do nickname (números após o último ' - ')"""
    if not nickname:
        return None
    
    # Procurar padrão: " - 123456"
    match = re.search(r' - (\d+)$', nickname)
    if match:
        return match.group(1)
    
    # Tentar padrão alternativo
    match = re.search(r'-(\d+)$', nickname)
    if match:
        return match.group(1)
    
    return None

async def atualizar_nickname(member: discord.Member):
    """Atualiza nickname mantendo a primeira parte fixa"""
    try:
        # Verificar permissões
        if not member.guild.me.guild_permissions.manage_nicknames:
            return False
        
        # Extrair partes do nickname atual
        nickname_atual = member.nick or member.name
        parte_nome = extrair_parte_nickname(nickname_atual)
        id_fivem = extrair_id_fivem(nickname_atual)
        
        # Encontrar cargo principal
        cargo_principal = None
        for cargo_nome in ORDEM_PRIORIDADE:
            if discord.utils.get(member.roles, name=cargo_nome):
                cargo_principal = cargo_nome
                break
        
        if not cargo_principal or cargo_principal not in NICKNAME_CONFIG:
            return False
        
        # Gerar novo nickname
        template = NICKNAME_CONFIG[cargo_principal]
        
        # Se o template não precisa de ID, usar versão sem ID
        if '{id}' not in template:
            novo_nick = template.format(name=parte_nome)
        else:
            # Se precisa de ID mas não tem, usar placeholder
            if not id_fivem:
                id_fivem = "000000"
            novo_nick = template.format(name=parte_nome, id=id_fivem)
        
        # Limitar a 32 caracteres
        if len(novo_nick) > 32:
            novo_nick = novo_nick[:32]
        
        # Aplicar se for diferente
        if member.nick != novo_nick:
            await member.edit(nick=novo_nick)
            return True
            
    except Exception:
        pass
    
    return False

# ========== SISTEMA CLEAN DE CARGO ==========
class CargoSelectView(ui.View):
    """View simples para selecionar cargo"""
    def __init__(self, member: discord.Member, action: str):
        super().__init__(timeout=60)
        self.member = member
        self.action = action  # "add" ou "remove"
        
        # Opções de cargo
        options = []
        cargos_disponiveis = [
            ("00", "Dono"),
            ("𝐀𝐃𝐌", "Administrador"),
            ("𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐄𝐥𝐢𝐭𝐞", "Gerente Elite"),
            ("𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "Gerente"),
            ("𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "Sublíder"),
            ("𝐄𝐥𝐢𝐭𝐞", "The bests"),
            ("𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Recrutador"),
            ("𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "Gerente de Família"),
            ("𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "Gerente de Recrutamento"),
            ("𝐌𝐨𝐝𝐞𝐫", "Moderador"),
            ("𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨", "Aviãozinho"),
            ("𝐌𝐞𝐦𝐛𝐫𝐨", "Membro"),
            ("𝐕𝐢𝐬𝐢𝐭𝐚𝐧𝐭𝐞", "Visitante"),
        ]
        
        for cargo_nome, desc in cargos_disponiveis:
            options.append(
                discord.SelectOption(
                    label=cargo_nome,
                    description=desc,
                    emoji=desc.split()[0]
                )
            )
        
        self.select = ui.Select(
            placeholder="Selecione o cargo...",
            options=options,
            custom_id="cargo_select"
        )
        self.select.callback = self.on_select
        self.add_item(self.select)
    
    async def on_select(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        cargo_nome = self.select.values[0]
        cargo = discord.utils.get(interaction.guild.roles, name=cargo_nome)
        
        if not cargo:
            msg = await interaction.followup.send("❌ Cargo não encontrado!", ephemeral=True)
            await asyncio.sleep(5)
            await msg.delete()
            return
        
        try:
            if self.action == "add":
                await self.member.add_roles(cargo)
                mensagem = f"✅ Cargo `{cargo.name}` adicionado para {self.member.mention}"
            else:
                await self.member.remove_roles(cargo)
                mensagem = f"✅ Cargo `{cargo.name}` removido de {self.member.mention}"
            
            # Atualizar nickname
            await atualizar_nickname(self.member)
            
            # Enviar mensagem temporária
            msg = await interaction.followup.send(mensagem, ephemeral=False)
            await asyncio.sleep(5)
            await msg.delete()
            
            # Deletar a mensagem com o select também
            await interaction.delete_original_response()
            
        except discord.Forbidden:
            msg = await interaction.followup.send("❌ Sem permissão!", ephemeral=True)
            await asyncio.sleep(5)
            await msg.delete()
        except Exception as e:
            msg = await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)
            await asyncio.sleep(5)
            await msg.delete()

# ========== MODAL SIMPLES ==========
class SimpleCargoModal(ui.Modal, title="🎯 Gerenciar Cargo"):
    """Modal simples para gerenciar cargo"""
    
    usuario_input = ui.TextInput(
        label="Usuário (@nome ou ID):",
        placeholder="Mencione o usuário ou cole o ID",
        required=True
    )
    
    def __init__(self, action: str):
        super().__init__()
        self.action = action  # "add" ou "remove"
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Verificar se é staff
        if not any(role.name in STAFF_ROLES for role in interaction.user.roles):
            msg = await interaction.followup.send("❌ Apenas staff pode usar!", ephemeral=True)
            await asyncio.sleep(5)
            await msg.delete()
            return
        
        # Encontrar usuário
        member = None
        input_text = self.usuario_input.value
        
        try:
            # Se for menção
            if "<@" in input_text:
                user_id = input_text.replace("<@", "").replace(">", "").replace("!", "")
                member = interaction.guild.get_member(int(user_id))
            
            # Se for ID numérico
            elif input_text.isdigit():
                member = interaction.guild.get_member(int(input_text))
            
            # Se for nome
            else:
                for guild_member in interaction.guild.members:
                    if input_text.lower() in guild_member.name.lower():
                        member = guild_member
                        break
            
            if not member:
                msg = await interaction.followup.send("❌ Usuário não encontrado!", ephemeral=True)
                await asyncio.sleep(5)
                await msg.delete()
                return
            
            # Mostrar view para selecionar cargo
            view = CargoSelectView(member, self.action)
            
            # Criar embed simples
            embed = discord.Embed(
                title=f"{'➕ Adicionar' if self.action == 'add' else '➖ Remover'} Cargo",
                description=f"Usuário: {member.mention}\nSelecione o cargo abaixo:",
                color=discord.Color.blue() if self.action == "add" else discord.Color.red()
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            msg = await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)
            await asyncio.sleep(5)
            await msg.delete()

# ========== VIEW DO PAINEL ==========
class CleanCargoView(ui.View):
    """View clean do painel de cargos"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="➕ Add Cargo", style=ButtonStyle.green, emoji="➕", custom_id="add_cargo_clean")
    async def add_cargo(self, interaction: discord.Interaction, button: ui.Button):
        # Verificar staff
        if not any(role.name in STAFF_ROLES for role in interaction.user.roles):
            msg = await interaction.response.send_message("❌ Apenas staff!", ephemeral=True)
            return
        
        modal = SimpleCargoModal("add")
        await interaction.response.send_modal(modal)
    
    @ui.button(label="➖ Rem Cargo", style=ButtonStyle.red, emoji="➖", custom_id="remove_cargo_clean")
    async def remove_cargo(self, interaction: discord.Interaction, button: ui.Button):
        # Verificar staff
        if not any(role.name in STAFF_ROLES for role in interaction.user.roles):
            msg = await interaction.response.send_message("❌ Apenas staff!", ephemeral=True)
            return
        
        modal = SimpleCargoModal("remove")
        await interaction.response.send_modal(modal)

# ========== COG PRINCIPAL ==========
class CargosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ Sistema de Cargos carregado!")
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Atualiza nickname quando cargo muda"""
        if before.roles != after.roles:
            await asyncio.sleep(1)
            await atualizar_nickname(after)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Carrega view persistente"""
        self.bot.add_view(CleanCargoView())
        print("✅ View de cargos carregada")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_cargos(self, ctx):
        """Cria painel clean de cargos"""
        
        embed = discord.Embed(
            title="⚙️ SISTEMA DE CARGOS",
            description=(
                "**Como funciona:**\n"
                "1. Clique em Add ou Rem\n"
                "2. Digite @usuário ou ID\n"
                "3. Selecione o cargo\n"
                "✅ Nickname atualiza automaticamente\n\n"
                "**📌 Importante:**\n"
                "• O nickname mantém a primeira parte\n"
                "• ID do FiveM é preservado após ' - '\n"
                "• Apenas staff pode usar"
            ),
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Exemplos de Nickname",
            value=(
                "• MEM | João - 123456\n"
                "• GER | Maria - 789012\n"
                "• AV | Pedro - 345678"
            ),
            inline=False
        )
        
        embed.add_field(
            name="👑 Staff Permitido",
            value="\n".join(STAFF_ROLES[:5]) + "\n...",
            inline=False
        )
        
        embed.set_footer(text="Sistema Clean • Mensagens auto-deletam em 5s")
        
        view = CleanCargoView()
        
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()
    
    @commands.command()
    async def fixnick(self, ctx, member: discord.Member = None):
        """Corrige nickname manualmente"""
        if member is None:
            member = ctx.author
        
        success = await atualizar_nickname(member)
        
        if success:
            msg = await ctx.send(f"✅ Nickname de {member.mention} corrigido!")
            await asyncio.sleep(5)
            await msg.delete()
        else:
            msg = await ctx.send(f"❌ Não foi possível corrigir o nickname")
            await asyncio.sleep(5)
            await msg.delete()

async def setup(bot):
    await bot.add_cog(CargosCog(bot))
