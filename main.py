import discord
from discord.ext import commands
import json
import re
from urllib.parse import urlparse

# ================================================
# BOT ANTI-LIEN LE PLUS PUISSANT
# Détection intelligente des liens (regex + urlparse)
# Configuration par serveur + ignorer salons/catégories + bypass rôles
# Embeds modernes, cohérents et jolies
# ================================================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== CONFIGURATION =====================
bot_token = ""          # Ton Token de bot
owner_id = 111111111111111  # ID du propriétaire du bot (global pour la liste des sites bloqués)

# Variables globales
blocked_sites = []      # Liste des domaines bloqués (normalisés)
blocked_set = set()     # Set pour recherche ultra-rapide
guild_configs = {}      # Configuration par serveur (clé = str(guild.id))

# ===================== FONCTIONS UTILITAIRES =====================
def normalize_domain(domain: str) -> str:
    """Normalise un domaine pour le stockage et la comparaison."""
    if not domain:
        return ""
    domain = domain.lower().strip()
    domain = domain.replace("https://", "").replace("http://", "")
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def has_blocked_link(content: str) -> bool:
    """Détection ultra-puissante des liens (avec ou sans protocole)."""
    if not blocked_set:
        return False

    domains = set()

    # 1. Liens avec protocole[](https://exemple.com)
    for url in re.findall(r'https?://[^\s<>"\']+', content, re.IGNORECASE):
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                domain = parsed.netloc.lower()
                if domain.startswith("www."):
                    domain = domain[4:]
                if domain:
                    domains.add(domain)
        except Exception:
            pass

    # 2. Domaines sans protocole (exemple.com, www.exemple.fr, discord.gg/abc)
    domain_pattern = r'\b(?:www\.)?([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+)\b'
    for match in re.findall(domain_pattern, content, re.IGNORECASE):
        if match:
            domains.add(match.lower())

    # Vérification ultra-rapide avec le set
    return bool(domains & blocked_set)


# ===================== CHARGEMENT DES FICHIERS =====================
# Chargement des sites bloqués (sites.json)
try:
    with open('sites.json', 'r', encoding='utf-8') as file:
        raw_sites = json.load(file)
        blocked_sites = [normalize_domain(s) for s in raw_sites if normalize_domain(s)]
        blocked_set = set(blocked_sites)
except FileNotFoundError:
    blocked_sites = []
    blocked_set = set()
    with open('sites.json', 'w', encoding='utf-8') as file:
        json.dump(blocked_sites, file, indent=4)
except Exception:
    blocked_sites = []
    blocked_set = set()

# Chargement de la config par serveur (config.json)
try:
    with open('config.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        guild_configs = data.get('guilds', {})
except FileNotFoundError:
    guild_configs = {}
except Exception:
    guild_configs = {}


def save_config():
    """Sauvegarde la configuration des serveurs."""
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump({'guilds': guild_configs}, file, indent=4)


def update_blocked_sites():
    """Sauvegarde la liste des sites bloqués."""
    with open('sites.json', 'w', encoding='utf-8') as file:
        json.dump(blocked_sites, file, indent=4)


# ===================== EVENTS =====================
@bot.event
async def on_ready():
    print(f'[+] Bot connecté en tant que {bot.user.name} | Anti-lien prêt et ultra-optimisé !')
    # by Fazer


@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild:
        await bot.process_commands(message)
        return

    guild_id = str(message.guild.id)
    config = guild_configs.get(guild_id)

    # Anti-lien désactivé ou jamais configuré → on passe
    if not config or not config.get("enabled", False):
        await bot.process_commands(message)
        return

    # 1. Bypass rôle ?
    if any(role.id in config.get("bypassed_roles", []) for role in message.author.roles):
        await bot.process_commands(message)
        return

    # 2. Salon ignoré ?
    if message.channel.id in config.get("ignored_channels", []):
        await bot.process_commands(message)
        return

    # 3. Catégorie ignorée ?
    if message.channel.category and message.channel.category.id in config.get("ignored_categories", []):
        await bot.process_commands(message)
        return

    # 4. Lien bloqué détecté ?
    if has_blocked_link(message.content):
        await message.delete()
        embed = discord.Embed(
            title="🚫 Site Bloqué Détecté",
            description=f"{message.author.mention}, ton message contient un lien bloqué.",
            color=discord.Color.red()
        )
        embed.set_footer(text="by Fazer • Système Anti-lien")
        await message.channel.send(embed=embed)

    await bot.process_commands(message)


# ===================== COMMANDES ANTI-LIEN =====================
@bot.group(name="antilien", invoke_without_command=True)
async def antilien(ctx):
    """Commande principale - Affiche l'aide complète."""
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🤖 Système Anti-Lien - Par Fazer",
            description=(
                "**Commandes disponibles :**\n\n"
                "`!antilien activer` → Active l'anti-lien sur le serveur\n"
                "`!antilien désactiver` → Désactive l'anti-lien\n"
                "`!antilien statut` → Voir le statut détaillé\n"
                "`!antilien bloquer <domaine>` → Ajoute un domaine bloqué (global)\n"
                "`!antilien débloquer <domaine>` → Retire un domaine bloqué\n"
                "`!antilien liste` → Liste complète des domaines bloqués\n\n"
                "**Configuration fine :**\n"
                "`!antilien ignorer-salon <salon>` → Ignore un salon\n"
                "`!antilien ignorer-catégorie <catégorie>` → Ignore une catégorie\n"
                "`!antilien bypass-rôle <rôle>` → Ajoute un rôle qui contourne l'anti-lien\n"
                "`!antilien autoriser-salon <salon>` → Réactive un salon\n"
                "`!antilien autoriser-catégorie <catégorie>` → Réactive une catégorie\n"
                "`!antilien retirer-bypass-rôle <rôle>` → Retire le bypass d'un rôle\n\n"
                "• Seul le **propriétaire du bot** peut gérer la liste des domaines.\n"
                "• Les **admins du serveur** peuvent configurer l'anti-lien."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Anti-lien le plus puissant • by Fazer")
        await ctx.send(embed=embed)


# --- Activation / Désactivation ---
@antilien.command(name="activer")
async def antilien_activer(ctx):
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Permission Refusée", description="Tu dois avoir la permission `Gérer le serveur` pour utiliser cette commande.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    if guild_id not in guild_configs:
        guild_configs[guild_id] = {
            "enabled": False,
            "ignored_channels": [],
            "ignored_categories": [],
            "bypassed_roles": []
        }

    if guild_configs[guild_id]["enabled"]:
        embed = discord.Embed(title="✅ Déjà Activé", description="L'anti-lien est déjà activé sur ce serveur.", color=discord.Color.green())
    else:
        guild_configs[guild_id]["enabled"] = True
        save_config()
        embed = discord.Embed(title="✅ Anti-lien Activé", description="L'anti-lien est maintenant **actif** sur tout le serveur.", color=discord.Color.green())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


@antilien.command(name="désactiver")
async def antilien_desactiver(ctx):
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Permission Refusée", description="Tu dois avoir la permission `Gérer le serveur` pour utiliser cette commande.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    if guild_id not in guild_configs:
        guild_configs[guild_id] = {
            "enabled": False,
            "ignored_channels": [],
            "ignored_categories": [],
            "bypassed_roles": []
        }

    if not guild_configs[guild_id]["enabled"]:
        embed = discord.Embed(title="❌ Déjà Désactivé", description="L'anti-lien est déjà désactivé sur ce serveur.", color=discord.Color.red())
    else:
        guild_configs[guild_id]["enabled"] = False
        save_config()
        embed = discord.Embed(title="✅ Anti-lien Désactivé", description="L'anti-lien est maintenant **désactivé** sur le serveur.", color=discord.Color.red())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


# --- Statut ---
@antilien.command(name="statut")
async def antilien_statut(ctx):
    guild_id = str(ctx.guild.id)
    config = guild_configs.get(guild_id, {"enabled": False, "ignored_channels": [], "ignored_categories": [], "bypassed_roles": []})

    status = "✅ **Activé**" if config["enabled"] else "❌ **Désactivé**"

    # Salons ignorés
    ignored_channels_str = ", ".join(f"<#{cid}>" for cid in config["ignored_channels"]) if config["ignored_channels"] else "Aucun"

    # Catégories ignorées (avec nom lisible)
    ignored_cats = []
    for cid in config.get("ignored_categories", []):
        cat = discord.utils.get(ctx.guild.categories, id=cid)
        name = cat.name if cat else f"Catégorie #{cid}"
        ignored_cats.append(f"• {name}")
    ignored_categories_str = "\n".join(ignored_cats) if ignored_cats else "Aucun"

    # Rôles bypass
    bypassed_roles_str = ", ".join(f"<@&{rid}>" for rid in config.get("bypassed_roles", [])) if config.get("bypassed_roles") else "Aucun"

    embed = discord.Embed(
        title="📊 Statut Anti-Lien",
        description=(
            f"**Statut global :** {status}\n\n"
            f"**Salons ignorés :** {ignored_channels_str}\n"
            f"**Catégories ignorées :**\n{ignored_categories_str}\n"
            f"**Rôles avec bypass :** {bypassed_roles_str}"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="by Fazer • Configuration du serveur")
    await ctx.send(embed=embed)


# --- Gestion globale des domaines bloqués (seul le propriétaire) ---
@antilien.command(name="bloquer")
async def antilien_bloquer(ctx, *, site: str):
    if ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Accès Refusé", description="Seul le propriétaire du bot peut gérer la liste des sites bloqués.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    norm_site = normalize_domain(site)
    if not norm_site or "." not in norm_site:
        embed = discord.Embed(title="❌ Domaine Invalide", description="Veuillez entrer un domaine valide (exemple : `google.com` ou `discord.gg`).", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if norm_site in blocked_set:
        embed = discord.Embed(title="❌ Déjà Bloqué", description=f"Le site `https://{norm_site}/` est déjà dans la liste.", color=discord.Color.red())
    else:
        blocked_sites.append(norm_site)
        blocked_set.add(norm_site)
        update_blocked_sites()
        embed = discord.Embed(title="✅ Site Bloqué", description=f"Le site `https://{norm_site}/` a été ajouté avec succès.", color=discord.Color.green())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


@antilien.command(name="débloquer")
async def antilien_debloquer(ctx, *, site: str):
    if ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Accès Refusé", description="Seul le propriétaire du bot peut gérer la liste des sites bloqués.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    norm_site = normalize_domain(site)
    if norm_site in blocked_set:
        blocked_sites.remove(norm_site)
        blocked_set.remove(norm_site)
        update_blocked_sites()
        embed = discord.Embed(title="✅ Site Débloqué", description=f"Le site `https://{norm_site}/` a été retiré.", color=discord.Color.green())
    else:
        embed = discord.Embed(title="❌ Non Trouvé", description=f"Le site `https://{norm_site}/` n'est pas dans la liste.", color=discord.Color.red())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


@antilien.command(name="liste")
async def antilien_liste(ctx):
    """Tout le monde peut voir la liste."""
    if not blocked_sites:
        formatted = "Aucun site bloqué pour le moment."
    else:
        formatted = "\n".join(f"https://{site}/" for site in blocked_sites)

    embed = discord.Embed(
        title="📋 Liste des Sites Bloqués",
        description=f"```\n{formatted}\n```",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"{len(blocked_sites)} domaine(s) bloqué(s) • by Fazer")
    await ctx.send(embed=embed)


# --- Configuration fine par serveur ---
@antilien.command(name="ignorer-salon")
async def antilien_ignorer_salon(ctx, channel: discord.TextChannel):
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Permission Refusée", description="Tu dois avoir la permission `Gérer le serveur`.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    if guild_id not in guild_configs:
        guild_configs[guild_id] = {"enabled": False, "ignored_channels": [], "ignored_categories": [], "bypassed_roles": []}

    config = guild_configs[guild_id]
    if channel.id in config["ignored_channels"]:
        embed = discord.Embed(title="❌ Déjà Ignoré", description=f"Le salon {channel.mention} est déjà ignoré.", color=discord.Color.red())
    else:
        config["ignored_channels"].append(channel.id)
        save_config()
        embed = discord.Embed(title="✅ Salon Ignoré", description=f"L'anti-lien ne s'appliquera **plus** dans {channel.mention}.", color=discord.Color.green())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


@antilien.command(name="autoriser-salon")
async def antilien_autoriser_salon(ctx, channel: discord.TextChannel):
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Permission Refusée", description="Tu dois avoir la permission `Gérer le serveur`.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    config = guild_configs.get(guild_id)
    if not config or channel.id not in config.get("ignored_channels", []):
        embed = discord.Embed(title="❌ Non Ignoré", description=f"Le salon {channel.mention} n'était pas ignoré.", color=discord.Color.red())
    else:
        config["ignored_channels"].remove(channel.id)
        save_config()
        embed = discord.Embed(title="✅ Salon Autorisé", description=f"L'anti-lien s'applique maintenant dans {channel.mention}.", color=discord.Color.green())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


@antilien.command(name="ignorer-catégorie")
async def antilien_ignorer_categorie(ctx, category: discord.CategoryChannel):
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Permission Refusée", description="Tu dois avoir la permission `Gérer le serveur`.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    if guild_id not in guild_configs:
        guild_configs[guild_id] = {"enabled": False, "ignored_channels": [], "ignored_categories": [], "bypassed_roles": []}

    config = guild_configs[guild_id]
    if category.id in config.get("ignored_categories", []):
        embed = discord.Embed(title="❌ Déjà Ignorée", description=f"La catégorie **{category.name}** est déjà ignorée.", color=discord.Color.red())
    else:
        config.setdefault("ignored_categories", []).append(category.id)
        save_config()
        embed = discord.Embed(title="✅ Catégorie Ignorée", description=f"L'anti-lien ne s'appliquera **plus** dans la catégorie **{category.name}**.", color=discord.Color.green())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


@antilien.command(name="autoriser-catégorie")
async def antilien_autoriser_categorie(ctx, category: discord.CategoryChannel):
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Permission Refusée", description="Tu dois avoir la permission `Gérer le serveur`.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    config = guild_configs.get(guild_id)
    if not config or category.id not in config.get("ignored_categories", []):
        embed = discord.Embed(title="❌ Non Ignorée", description=f"La catégorie **{category.name}** n'était pas ignorée.", color=discord.Color.red())
    else:
        config["ignored_categories"].remove(category.id)
        save_config()
        embed = discord.Embed(title="✅ Catégorie Autorisée", description=f"L'anti-lien s'applique maintenant dans la catégorie **{category.name}**.", color=discord.Color.green())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


@antilien.command(name="bypass-rôle")
async def antilien_bypass_role(ctx, role: discord.Role):
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Permission Refusée", description="Tu dois avoir la permission `Gérer le serveur`.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    if guild_id not in guild_configs:
        guild_configs[guild_id] = {"enabled": False, "ignored_channels": [], "ignored_categories": [], "bypassed_roles": []}

    config = guild_configs[guild_id]
    if role.id in config.get("bypassed_roles", []):
        embed = discord.Embed(title="❌ Déjà Bypass", description=f"Le rôle {role.mention} contourne déjà l'anti-lien.", color=discord.Color.red())
    else:
        config.setdefault("bypassed_roles", []).append(role.id)
        save_config()
        embed = discord.Embed(title="✅ Bypass Ajouté", description=f"Le rôle {role.mention} contourne maintenant l'anti-lien.", color=discord.Color.green())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


@antilien.command(name="retirer-bypass-rôle")
async def antilien_retirer_bypass_role(ctx, role: discord.Role):
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != owner_id:
        embed = discord.Embed(title="🚫 Permission Refusée", description="Tu dois avoir la permission `Gérer le serveur`.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    config = guild_configs.get(guild_id)
    if not config or role.id not in config.get("bypassed_roles", []):
        embed = discord.Embed(title="❌ Non Bypass", description=f"Le rôle {role.mention} ne contourne pas l'anti-lien.", color=discord.Color.red())
    else:
        config["bypassed_roles"].remove(role.id)
        save_config()
        embed = discord.Embed(title="✅ Bypass Retiré", description=f"Le rôle {role.mention} ne contourne plus l'anti-lien.", color=discord.Color.green())
    embed.set_footer(text="by Fazer")
    await ctx.send(embed=embed)


# ===================== LANCEMENT DU BOT =====================
bot.run(bot_token)
