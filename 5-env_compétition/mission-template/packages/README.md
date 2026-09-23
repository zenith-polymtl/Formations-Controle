# packages/ : les paquets partagés

Un paquet est **local** à sa mission (dans `workspaces/<mission>_ws/src/`) sauf s'il sert ailleurs. S'il sert à deux workspaces de ce dépôt, il vit ici comme dossier simple (`sim_mocks`). S'il sert à deux dépôts (aeac-2027 et SUAS, ou d'une année à l'autre), il vit ici comme sous-module, et c'est un lead qui le décide.

| Paquet | Type | Rôle |
|---|---|---|
| `custom_interfaces` | sous-module | Messages, services, et constantes d'enum (états, modes, PWM) |
| `tools` | sous-module | `topics.py` (la table des noms de topics), heartbeats, utilitaires |
| `nav_stack` | sous-module | Initialisation, conversions GPS et local, waypoints |
| `vision` | sous-module | Pipeline ZED et YOLO (conteneur vision) |
| `zed-ros2-wrapper` | sous-module tiers, fork `zenith` | Wrapper ZED ; hors des workspaces, construit à part dans son image |
| `sim_mocks` | dossier | Ce qui remplace le matériel en simulation |

Un workspace utilise un paquet partagé par un symlink dans son `src/` : `make link C=<mission> PKG=<paquet>`, puis on commet le lien. `ls -l workspaces/<mission>_ws/src` dit ce que la mission utilise et ce qui est partagé.

Sous-modules, trois choses à savoir : on clone avec `--recurse-submodules` ; `make init` rattrape si on a oublié ; si `make status` dit qu'un sous-module est modifié localement, demander à un lead avant de continuer. Le reste (`make bump`, créer un sous-module) est dans `ARCHITECTURE.md`, section leads.
