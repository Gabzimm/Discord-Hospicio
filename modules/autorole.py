import discord
from discord.ext import commands
import asyncio

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_role_name = "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨"
        print(f"🛬 AutoRole iniciado | Cargo alvo: {self.target_role_name}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Quando um membro entra no servidor"""
        print(f"🎯 EVENTO DISPARADO: {member.name} entrou no servidor {member.guild.name}")
        
        try:
            # Buscar o cargo
            role = discord.utils.get(member.guild.roles, name=self.target_role_name)
            
            if not role:
                print(f"❌ CARGO NÃO ENCONTRADO: '{self.target_role_name}'")
                return
            
            print(f"✅ Cargo encontrado: {role.name} (ID: {role.id})")
            
            # Verificar permissões do bot
            bot_member = member.guild.get_member(self.bot.user.id)
            if not bot_member.guild_permissions.manage_roles:
                print("❌ Bot SEM permissão 'manage_roles'")
                return
            
            # Verificar hierarquia
            bot_top_role = bot_member.top_role
            if bot_top_role.position <= role.position:
                print(f"❌ Hierarquia inválida: Bot role ({bot_top_role.position}) ≤ Target role ({role.position})")
                return
            
            # Dar o cargo (com timeout)
            try:
                await member.add_roles(role, reason="Auto-role: entrada no servidor")
                print(f"✅ SUCESSO: Cargo dado para {member.name}")
                
                # Log no canal de logs se existir
                log_channel = discord.utils.get(member.guild.text_channels, name="logs")
                if log_channel:
                    embed = discord.Embed(
                        title="🛬 Novo Membro",
                        description=f"{member.mention} entrou no servidor",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Cargo dado", value=role.mention)
                    embed.set_footer(text=f"ID: {member.id}")
                    await log_channel.send(embed=embed)
                    
            except discord.Forbidden:
                print("❌ FORBIDDEN: Sem permissão para dar cargo")
            except Exception as e:
                print(f"❌ ERRO ao dar cargo: {type(e).__name__}: {e}")
                
        except Exception as e:
            print(f"❌ ERRO GERAL em on_member_join: {type(e).__name__}: {e}")
    
    @commands.command()
    async def test_autorole(self, ctx, member: discord.Member = None):
        """Testa manualmente o autorole"""
        if member is None:
            member = ctx.author
        
        # Simular o evento
        await self.on_member_join(member)
        await ctx.send(f"✅ Teste realizado para {member.mention}")
    
    @commands.command()
    async def autorole_status(self, ctx):
        """Mostra status completo do autorole"""
        embed = discord.Embed(
            title="🛬 Status do Auto-Role",
            color=discord.Color.blue()
        )
        
        # 1. Verificar cargo
        role = discord.utils.get(ctx.guild.roles, name=self.target_role_name)
        if role:
            embed.add_field(name="✅ Cargo", value=f"`{role.name}` (ID: {role.id})", inline=False)
        else:
            embed.add_field(name="❌ Cargo", value=f"Não encontrado: `{self.target_role_name}`", inline=False)
        
        # 2. Verificar permissões do bot
        bot_member = ctx.guild.get_member(self.bot.user.id)
        perms = bot_member.guild_permissions
        
        if perms.manage_roles:
            embed.add_field(name="✅ Permissão", value="`manage_roles` = SIM", inline=True)
        else:
            embed.add_field(name="❌ Permissão", value="`manage_roles` = NÃO", inline=True)
        
        # 3. Verificar hierarquia
        if role and perms.manage_roles:
            bot_top_role = bot_member.top_role
            if bot_top_role.position > role.position:
                embed.add_field(name="✅ Hierarquia", value=f"Bot ({bot_top_role.position}) > Cargo ({role.position})", inline=True)
            else:
                embed.add_field(name="❌ Hierarquia", value=f"Bot ({bot_top_role.position}) ≤ Cargo ({role.position})", inline=True)
        
        # 4. Verificar intents
        embed.add_field(name="🎯 Intents", value=f"members={self.bot.intents.members}", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give_autorole(self, ctx, member: discord.Member):
        """Dá o cargo manualmente"""
        role = discord.utils.get(ctx.guild.roles, name=self.target_role_name)
        
        if not role:
            await ctx.send(f"❌ Cargo `{self.target_role_name}` não encontrado!")
            return
        
        try:
            await member.add_roles(role)
            await ctx.send(f"✅ Cargo `{role.name}` dado para {member.mention}!")
        except Exception as e:
            await ctx.send(f"❌ Erro: `{type(e).__name__}: {e}`")

async def setup(bot):
    await bot.add_cog(AutoRole(bot))
    print("✅ Módulo Auto-Role carregado com diagnóstico!")
