import discord
from discord.ext import commands
import asyncio

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_role_name = "𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨"
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Quando um membro entra no servidor"""
        print(f"👤 {member.name} entrou no servidor")
        
        try:
            # Buscar o cargo
            role = discord.utils.get(member.guild.roles, name=self.target_role_name)
            
            if role:
                # Dar o cargo
                await member.add_roles(role)
                print(f"✅ Cargo '{self.target_role_name}' dado para {member.name}")
                
                # Opcional: Enviar mensagem de boas-vindas
                try:
                    embed = discord.Embed(
                        title=f"👋 Bem-vindo(a) ao {member.guild.name}!",
                        description=(
                            f"Olá {member.mention}! 🎉\n"
                            f"Você recebeu automaticamente o cargo **{self.target_role_name}**!\n\n"
                            "**📌 Informações importantes:**\n"
                            "• Leia as regras em <#canal-das-regras>\n"
                            "• Conheça nossos canais\n"
                            "• Divirta-se!"
                        ),
                        color=discord.Color.green()
                    )
                    embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
                    
                    # Tentar enviar DM
                    await member.send(embed=embed)
                except:
                    # Se não conseguir DM, enviar no canal de boas-vindas
                    welcome_channel = discord.utils.get(member.guild.text_channels, name="boas-vindas")
                    if welcome_channel:
                        await welcome_channel.send(f"{member.mention}", embed=embed)
                        
            else:
                print(f"❌ Cargo '{self.target_role_name}' não encontrado!")
                
        except Exception as e:
            print(f"❌ Erro ao dar cargo: {e}")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_autorole(self, ctx):
        """Configura o sistema de auto-role"""
        embed = discord.Embed(
            title="🛬 Auto-Role Configurado",
            description=(
                f"✅ Sistema de auto-role ativado!\n\n"
                f"**Cargo atribuído automaticamente:** `{self.target_role_name}`\n"
                f"**Status:** 🟢 Ativo\n\n"
                f"*Novos membros receberão este cargo ao entrar.*"
            ),
            color=discord.Color.blue()
        )
        
        # Verificar se o cargo existe
        role = discord.utils.get(ctx.guild.roles, name=self.target_role_name)
        if not role:
            embed.add_field(
                name="⚠️ Atenção",
                value=f"Cargo `{self.target_role_name}` não encontrado!\nCrie o cargo para o sistema funcionar.",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def check_autorole(self, ctx):
        """Verifica configuração do auto-role"""
        role = discord.utils.get(ctx.guild.roles, name=self.target_role_name)
        
        embed = discord.Embed(
            title="🔍 Status do Auto-Role",
            color=discord.Color.gold()
        )
        
        if role:
            embed.description = f"✅ Cargo `{self.target_role_name}` encontrado!"
            embed.add_field(name="🆔 ID", value=f"`{role.id}`", inline=True)
            embed.add_field(name="🎨 Cor", value=str(role.color), inline=True)
            embed.add_field(name="👥 Membros", value=len(role.members), inline=True)
            embed.set_footer(text="Sistema funcionando corretamente!")
        else:
            embed.description = f"❌ Cargo `{self.target_role_name}` NÃO encontrado!"
            embed.add_field(
                name="📝 Solução",
                value="1. Crie o cargo manualmente\n2. Certifique-se do nome exato\n3. O bot precisa ter permissão para dar cargos",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give_all_autorole(self, ctx):
        """Dá o cargo para TODOS os membros atuais"""
        role = discord.utils.get(ctx.guild.roles, name=self.target_role_name)
        
        if not role:
            await ctx.send(f"❌ Cargo `{self.target_role_name}` não encontrado!")
            return
        
        members_without_role = [m for m in ctx.guild.members if role not in m.roles]
        
        if not members_without_role:
            await ctx.send("✅ Todos os membros já têm este cargo!")
            return
        
        embed = discord.Embed(
            title="🔄 Atribuindo cargo a todos",
            description=f"Dando `{self.target_role_name}` para {len(members_without_role)} membro(s)...",
            color=discord.Color.orange()
        )
        
        msg = await ctx.send(embed=embed)
        
        success = 0
        failed = 0
        
        for member in members_without_role:
            try:
                await member.add_roles(role)
                success += 1
            except:
                failed += 1
            await asyncio.sleep(0.5)  # Evitar rate limit
        
        embed = discord.Embed(
            title="✅ Concluído!",
            description=(
                f"**Cargo:** `{self.target_role_name}`\n"
                f"**✅ Sucesso:** {success} membro(s)\n"
                f"**❌ Falhas:** {failed} membro(s)\n"
                f"**Total processado:** {len(members_without_role)}"
            ),
            color=discord.Color.green()
        )
        
        await msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoRole(bot))
    print("✅ Módulo Auto-Role carregado!")
