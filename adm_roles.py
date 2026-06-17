import discord
import json
import os

# ========== ARQUIVO DE CONFIGURAÇÃO ==========
DATA_FILE = "adm_roles.json"

def load_adm_roles(guild_id=None):
    """Carrega lista de cargos ADM"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and guild_id:
                    return data.get(str(guild_id), [])
                elif isinstance(data, list):
                    return data
                return []
        except:
            return []
    return []

def save_adm_roles(roles, guild_id=None):
    """Salva lista de cargos ADM"""
    try:
        existing_data = {}
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, dict):
                        existing_data = {}
            except:
                existing_data = {}
        
        if guild_id:
            existing_data[str(guild_id)] = roles
        else:
            existing_data = roles
        
        with open(DATA_FILE, "w") as f:
            json.dump(existing_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar ADM roles: {e}")
        return False

def is_staff(member: discord.Member) -> bool:
    """Verifica se o membro tem permissão de staff"""
    if not member:
        return False
    
    if member.id == member.guild.owner_id:
        return True
    
    for role in member.roles:
        if role.name == "𝐎𝐰𝐧𝐞𝐫":
            return True
    
    if member.guild_permissions.administrator:
        return True
    
    adm_roles = load_adm_roles(member.guild.id)
    for role in member.roles:
        if role.name in adm_roles:
            return True
    
    return False

def can_use_adm(member: discord.Member) -> bool:
    """Quem pode usar !adm: Dono OU cargo 𝐎𝐰𝐧𝐞𝐫"""
    if not member:
        return False
    
    if member.id == member.guild.owner_id:
        return True
    
    for role in member.roles:
        if role.name == "𝐎𝐰𝐧𝐞𝐫":
            return True
    
    return False
