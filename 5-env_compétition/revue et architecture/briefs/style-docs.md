# Style commun des documents de la formation 5 (à lire avant d'écrire)

Public : une recrue de l'équipe contrôle de Zenith (club de drones de Polytechnique Montréal) qui a fait les formations 2 (WSL, Docker, Compose, Make) et 3 (ROS 2, mavros, projet de pilotage au clavier). Elle lit seule, sur GitHub, et poste ses jalons sur Discord.

Modèles à imiter, dans `C:\Users\colin\Zenith\Control-Formations` : `3-ros2\3.4-piloter-au-clavier.md` (structure complète : titre, « Objectifs de la formation », prérequis, bloc `> [!NOTE] **Avant de commencer**` avec Durée / Prérequis / À la fin / Aide / À poster à la fin, sections numérotées `## 1 - Titre` et `### 1.1 - Sous-titre`, jalons en gras « Jalon : ... », blocs `<details>` pour les apartés, table « Quand ça casse » à la fin) et `2-environnement\2-wsl-docker-compose-make.md` (ton, longueur des paragraphes, encadrés `> [!NOTE]`). Lis les 150 premières lignes de chacun avant d'écrire.

Règles d'écriture de Colin, non négociables :
- Vouvoiement (« vous »), comme dans les formations 2 et 3.
- Jamais de tiret cadratin (—) ni de tiret demi-cadratin en incise. Utiliser la virgule, les deux-points ou le point.
- Pas de « look IA » : pas de listes à puces en cascade pour tout dire, pas de phrases creuses d'introduction ou de conclusion (« Dans cette section nous allons... », « Félicitations ! »), pas de gras sur des phrases entières, pas d'émojis. Des paragraphes courts, du concret, une commande puis ce qu'elle a fait.
- Une commande par bloc ```bash quand la recrue doit la taper ; la sortie attendue en dessous quand elle sert à se repérer.
- Les fichiers du dépôt sont cités en `code` ; les liens vers d'autres documents de la formation sont des liens Markdown relatifs.
- Français partout dans la prose ; les noms de code, topics, cibles make restent en anglais tels quels.
- Ne rien inventer sur le dépôt : chaque commande, chaque fichier, chaque nom de topic cité doit exister dans `C:\Users\colin\Zenith\aeac-2027` (ou dans `demo_ws` et le matériel de la formation). Vérifie en ouvrant les fichiers. Si le plan demande quelque chose que le dépôt n'a pas, écris le document pour ce que le dépôt fait vraiment et signale l'écart dans ton rapport.
- Les captures d'écran ne sont pas disponibles : là où le plan en prévoit une, mets un commentaire HTML `<!-- capture : make status -->` à l'endroit voulu, et liste-les dans le rapport.

Décisions déjà prises (ne pas rouvrir) :
- La recrue clone un dépôt de cohorte, `https://github.com/zenith-polymtl/formation-5-<cohorte>` (écrire `formation-5-automne-2026` dans les commandes), créé par un lead à partir d'aeac-2027 ; c'est là qu'elle pousse sa branche et ouvre sa PR en 5.3. aeac-2027 lui-même n'est jamais modifié par la formation.
- Le simulateur est le SITL de Mission Planner (formation 1), pas Gazebo. La formation 4 n'est pas requise.
- La formation vision est citée comme « à venir », sans numéro.
- La formation 6 (réseau, Zenoh, services, capteurs) suit ; la 5 doit tenir sans elle.
- Le dossier de la formation dans le dépôt Formations-Controle est `5-env_compétition/` et contient : `demo_ws/`, `pannes/`, `5.3-projet/`, `objectifs.md`, `mission-template/` (le squelette dont aeac-2027 est issu), `revue et architecture/` (documents de travail, pas pour la recrue).
