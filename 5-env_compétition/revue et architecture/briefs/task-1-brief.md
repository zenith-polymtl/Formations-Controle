# Tâche 1 : restructurer `tools` et `custom_interfaces` pour aeac-2027

Contexte : Zenith (club de drones de Polytechnique) prépare le dépôt de mission `C:\Users\colin\Zenith\aeac-2027` (chemin WSL : /mnt/c/Users/colin/Zenith/aeac-2027 ; sous Git Bash : /c/Users/colin/Zenith/aeac-2027). Ses paquets partagés sont des sous-modules git dans `packages/`. L'étape 1 du plan d'architecture V3 exige, pour `tools` et `custom_interfaces` : un paquet ROS 2 à la racine du dépôt (aujourd'hui il est dans un sous-dossier du même nom), métadonnées remplies, dossier `test/` supprimé, `tools/tools/topics.py` et des constantes d'état dans `custom_interfaces`. Rien n'est poussé sur GitHub : tout se passe sur une branche locale `aeac-2027` dans chaque sous-module, et aeac-2027 pointe ensuite sur ces commits.

Lis d'abord : `aeac-2027/ARCHITECTURE.md` (règles de code), `aeac-2027/packages/README.md`, `aeac-2027/scripts/check.py`, `aeac-2027/workspaces/gcs_ws/src/gcs_bringup/launch/base.launch.py`, et tout le contenu actuel de `packages/tools` et `packages/custom_interfaces`.

## À faire dans `packages/tools` (dépôt git à part, remote github.com/zenith-polymtl/tools)

1. `git switch -c aeac-2027` depuis le HEAD actuel (détaché).
2. Déplacer avec `git mv` le contenu de `tools/` (le sous-dossier paquet) à la racine du dépôt : `package.xml`, `setup.py`, `setup.cfg`, `resource/`, et le module Python `tools/` (qui contient `gcs_heartbeat.py`, `drone_heartbeat.py`, `__init__.py`). Résultat : `packages/tools/package.xml`, `packages/tools/setup.py`, `packages/tools/tools/__init__.py`, etc. Supprimer `test/` (`git rm -r`). Retirer les `test_depend` et `extras_require['test']`.
3. Métadonnées, dans `package.xml` ET `setup.py` : maintainer `Colin Cormier` email `colinc131@gmail.com`, licence `Apache-2.0`, description en anglais d'une ligne (« Shared ROS 2 utilities for Zenith mission repos: topic names, heartbeats »), version `1.0.0`. `package.xml` déclare `rclpy`, `std_msgs`, `mavros_msgs`, `custom_interfaces` (les imports réels des deux heartbeats ; vérifie-les).
4. Créer `tools/topics.py` : table plate de constantes, deux groupes séparés par un commentaire, aucune fonction, docstring de haut niveau en français. Contenu exact :
   ```python
   EXTERNAL = '/aeac/external'   # traverse la radio (Zenoh)
   INTERNAL = '/aeac/internal'   # reste sur la machine

   # --- Externes : vus par le sol ---
   GCS_HEARTBEAT = f'{EXTERNAL}/gcs/heartbeat'
   DRONE_HEALTH = f'{EXTERNAL}/drone/health'
   DEMO_STATE = f'{EXTERNAL}/demo/state'

   # --- Internes : drone seulement ---
   LINK_OK = f'{INTERNAL}/link_ok'
   ```
   Ajouter en tête un commentaire de trois lignes : un nom de topic s'écrit ici et nulle part ailleurs ; le deuxième segment décide seul de ce qui traverse la radio ; on ajoute une ligne par PR dans ce dépôt.
5. `gcs_heartbeat.py` et `drone_heartbeat.py` : la valeur par défaut du paramètre `topic_name` devient `topics.GCS_HEARTBEAT` et `topics.DRONE_HEALTH` (`from tools import topics` ou `from tools.topics import ...`). Corriger le log de `drone_heartbeat` qui dit « GCS Heartbeat » et passer les deux logs de démarrage en français. Ne rien changer d'autre à leur logique.
6. Commit sur `aeac-2027`, message en anglais, une ligne, par exemple `Move package to repo root, add topics.py, fill metadata`. Pas de ligne Co-Authored-By, aucune mention d'IA.

## À faire dans `packages/custom_interfaces` (remote github.com/zenith-polymtl/custom_interfaces)

1. `git switch -c aeac-2027`.
2. `git mv` du contenu de `custom_interfaces/` (`CMakeLists.txt`, `package.xml`, `msg/`, `srv/`) à la racine. `git rm empty.txt`. Retirer les `test_depend` ament_lint du `package.xml` et tout bloc `if(BUILD_TESTING)` du CMakeLists.
3. Métadonnées comme pour tools (description : « Shared ROS 2 messages, services and constants for Zenith mission repos »).
4. Ajouter `msg/MissionState.msg` :
   ```
   # État courant d'une mission. Les constantes sont la seule définition des états :
   # aucun nœud ne redéfinit ces valeurs (règle P17).
   uint8 IDLE=0
   uint8 GOTO=1
   uint8 ACT=2
   uint8 RETURN=3

   std_msgs/Header header
   uint8 state
   float32 time_in_state   # secondes passées dans l'état courant
   ```
   L'enregistrer dans le CMakeLists (les deux listes, si le fichier en a deux ; sinon la seule).
5. Commit sur `aeac-2027`, une ligne en anglais.

## À faire dans `aeac-2027`

1. Les symlinks `workspaces/gcs_ws/src/tools` et `.../custom_interfaces` pointent sur `../../../packages/<pkg>` : ils restent valides. Vérifie qu'ils n'ont pas besoin de changer (sous Windows ils sont des fichiers texte, c'est attendu).
2. `packages/README.md` : si une phrase décrit l'ancienne disposition (paquet dans un sous-dossier), la corriger. Ajouter une ligne : `tools/topics.py` est la table des topics, `custom_interfaces/msg/MissionState.msg` porte les états de mission.
3. Lancer `python3 scripts/check.py` (ou `python scripts/check.py` sous Windows) depuis la racine d'aeac-2027 : il doit sortir sans problème signalé pour `tools` et `custom_interfaces`. Les problèmes qu'il signale sur `nav_stack`, `vision` ou `zed-ros2-wrapper` sont hors périmètre : note-les dans le rapport sans les corriger.
4. `git add packages/tools packages/custom_interfaces packages/README.md` puis un commit dans aeac-2027 : `Point tools and custom_interfaces at aeac-2027 branches`. Ne pousse rien, nulle part.

## Vérification attendue dans le rapport

- `git -C packages/tools log --oneline -3` et `git -C packages/tools status --short` (propre), idem custom_interfaces.
- `python3 -c "import ast,sys; ast.parse(open('packages/tools/tools/topics.py').read())"` et compilation des deux heartbeats (`python3 -m py_compile`).
- Sortie complète de `scripts/check.py`.
- `find packages/tools packages/custom_interfaces -not -path '*/.git/*' -type f` après coup.
- Docker n'est pas disponible : aucun `colcon build` ne sera fait. Dis-le explicitement.

## Contraintes globales

- Aucun tiret cadratin (—) dans ce que tu écris. Français dans les docs et commentaires de haut niveau, anglais dans le code, les noms et les commits.
- Ne modifie pas `nav_stack`, `vision`, `zed-ros2-wrapper`, ni `Control-Formations/5-env_compétition/mission-template/`.
- Aucun `git push`.
