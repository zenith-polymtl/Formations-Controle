# Tâche 4 : rédiger le document 5.1, « Le dépôt vu de haut »

Fichier à créer : `C:\Users\colin\Zenith\Control-Formations\5-env_compétition\5.1-le-depot-vu-de-haut.md`

Lis dans l'ordre :
1. `style-docs.md` (même dossier que ce brief) : style et décisions.
2. Le plan, section 0 (lignes 13 à 52) et section 2 (lignes 68 à 149) de `C:\Users\colin\Zenith\Control-Formations\5-env_compétition\revue et architecture\PLAN-FORMATION-5.md`. La section 2 est ta spécification : objectifs, bloc « avant de commencer », les cinq sections, les jalons, la table « Quand ça casse ». Reprends sa structure et son contenu ; développe chaque section en prose de formation, pas en notes.
3. Le dépôt `C:\Users\colin\Zenith\aeac-2027` : `README.md`, `ARCHITECTURE.md` (tout), `Makefile` (tout, c'est ce que la recrue lit avec `make help`), `packages/README.md`, `config/README.md`, `compose/dev.yml`, `docker/dockerfile.gcs` (l'en-tête), `systemd/install.md` (le début), `workspaces/gcs_ws/src/gcs_bringup/launch/base.launch.py`, `packages/tools/tools/topics.py`, `packages/tools/tools/gcs_heartbeat.py` (le nom du topic du heartbeat, qui est le premier topic que la recrue observe).
4. `C:\Users\colin\Zenith\Control-Formations\5-env_compétition\objectifs.md`.

Points précis à respecter :
- Section 1 : la recrue lit `ARCHITECTURE.md` du dépôt cloné (donc le clone vient AVANT la lecture ; réordonne : la commande `git clone --recurse-submodules` est donnée dès le bloc « avant de commencer » ou au tout début de la section 1, et le reste de la section 4 du plan, `make init`, `make status`, `make build`, `make dev`, reste en section 4). Dis-le explicitement dans le document : « on clone maintenant, on comprend après ».
- Section 2 : la table de visite du dépôt reprend les neuf lignes du plan, reformulées en prose de formation ; les sept dossiers à réciter sont `docker/`, `compose/`, `config/`, `packages/`, `scripts/`, `systemd/`, `workspaces/`.
- Section 3 : montrer la sortie réelle de `make help` (reconstruis-la à partir du Makefile : les trois en-têtes `##@` et les cibles avec leur commentaire `##`, dans l'ordre du fichier) et les trois variables.
- Section 4 : chaque commande avec une phrase sur ce qu'elle a fait ; la sortie de `make status` reconstruite d'après la cible `status` du Makefile (branche, `git submodule status` avec cinq lignes). Les trois phrases sur les sous-modules, textuellement celles d'`ARCHITECTURE.md`. Le jalon : `ros2 launch gcs_bringup base.launch.py` dans le conteneur, puis `make shell IMG=dev` dans un second terminal et `ros2 topic echo` sur le topic du heartbeat (son nom exact vient de `topics.py`). Précise le `source install/setup.bash` si le conteneur `dev` ne le fait pas tout seul (vérifie `compose/dev.yml` et le Dockerfile ; si rien ne source, la recrue doit le faire et tu l'écris).
- Section 5 : les règles du README, lues à voix haute ; les deux à retenir ; où écrire.
- Table « Quand ça casse » : les quatre lignes du plan, plus toute ligne que la lecture du dépôt te suggère (par exemple `make sim` lancé au lieu de `make dev`).
- Durée annoncée : 1 h 45. À poster : photo du schéma dessiné à la main et capture de `make status`.
- Pas de section sur `systemd` au-delà des deux phrases de la table (la formation 6 l'ouvre).
- Termine par une ligne « Suite : [Formation 5.2](5.2-une-mission-en-simulation.md) ».

Rapport : liste des captures prévues (commentaires HTML), écarts entre le plan et le dépôt réel que tu as dû trancher, `wc -w` du document.

Contraintes : aucun tiret cadratin ; aucun commit ; ne modifie aucun autre fichier.
