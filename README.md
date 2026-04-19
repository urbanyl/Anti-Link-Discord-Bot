# 🤖 Anti-Lien Discord - By Fazer

Le bot anti-lien le plus puissant et complet pour Discord, entièrement en français.

### Fonctionnalités principales
- Détection intelligente des liens (https, http, sans protocole, sous-domaines…)
- Liste globale de sites bloqués
- Configuration fine par serveur
- Embeds modernes et stylés
- Code optimisé

### Toutes les commandes

#### Commandes principales
| Commande                    | Description |
|----------------------------|-----------|
| `!antilien`                | Affiche l’aide complète |
| `!antilien activer`        | Active l’anti-lien sur le serveur |
| `!antilien désactiver`     | Désactive l’anti-lien sur le serveur |
| `!antilien statut`         | Affiche le statut détaillé de la configuration |

#### Gestion des sites bloqués (propriétaire du bot uniquement)
| Commande                        | Description |
|--------------------------------|-----------|
| `!antilien bloquer <domaine>`  | Ajoute un domaine à la liste bloquée (ex: `google.com`) |
| `!antilien débloquer <domaine>`| Retire un domaine de la liste bloquée |
| `!antilien liste`              | Affiche la liste complète des sites bloqués |

#### Configuration par serveur (Admins)
| Commande                                | Description |
|----------------------------------------|-----------|
| `!antilien ignorer-salon #salon`       | Ignore un salon (l’anti-lien ne s’applique plus dedans) |
| `!antilien autoriser-salon #salon`     | Réactive l’anti-lien dans un salon |
| `!antilien ignorer-catégorie #catégorie`| Ignore une catégorie entière |
| `!antilien autoriser-catégorie #catégorie` | Réactive l’anti-lien dans une catégorie |
| `!antilien bypass-rôle @rôle`          | Ajoute un rôle qui contourne l’anti-lien |
| `!antilien retirer-bypass-rôle @rôle`  | Retire le bypass d’un rôle |

### Installation

1. Clone ce repository
2. Installe les dépendances :
   ```bash
   pip install -r requirements.txt
     ```
3. Mets ton token et ton owner_id dans le fichier bot.py
4. Lance le bot :
   ```bash
   python bot.py
     ```

   
