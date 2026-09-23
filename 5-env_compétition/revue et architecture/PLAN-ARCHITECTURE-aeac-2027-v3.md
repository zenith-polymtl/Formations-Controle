# Plan d'architecture aeac-2027, version 3

*21 septembre 2026. **Approuvée par Colin le 21 septembre 2026.** Version de référence après deux passes de revue (V1 : section 15 de la V2 ; V2 : section 15 ci-dessous). Toutes les explorations sont tranchées et fondues dans les propositions. Ce document est le plan du dépôt `aeac-2027` et du dossier `mission-template/` dont il sera la copie, et le fil de la future Formation 5. Il part de la branche de compétition d'aeac-2026 (`mission-2-photo-pipeline`, `71408c4`) et de sa revue pédagogique. Les documents `BRAINSTORM-partage-de-code-2027.md` et `EXPLORATION-*.md` restent comme trace des options écartées.*

**Fil directeur des décisions** : simple à comprendre et à implémenter, proche de ce qui marchait en 2026, sans mécanisme de plus que nécessaire pour une recrue.

**Décisions** : squelette générique seulement ; code en anglais, docs et logs en français ; template dans `Control-Formations/5-env_compétition/mission-template/` ; sous-modules simplifiés (`custom_interfaces`, `tools`, `nav_stack`, `vision`, `zed-ros2-wrapper`) pilotés par des cibles Make ; dépôts partagés repris et restructurés ; une mission = un workspace, symlinks versionnés ; un Dockerfile complet par rôle, dépendances Python en ligne comme en 2026 ; Makefile en trois sections (développement et simulation, test sur véhicule, déploiement) et systemd jamais seule voie ; `make sim` réduit à un paramètre `sim` et aux mocks ; SITL externe (Mission Planner) comme référence ; mission démo dans la formation 5 ; `gcs_ws` sert de workspace de développement, le conteneur de dev voit tout le dépôt ; pas de workspace `sim` ; SUAS 2027 dans un dépôt séparé ; le dépôt garde le nom `aeac-2027` ; `main` = ce qui vole ; pas de tests ; root dans les conteneurs à court terme.

**Hypothèses.** Même matériel qu'en 2026 (Jetson Orin, ZED, SIYI HM30, LTE + Tailscale, portable GCS sous WSL, deux drones). Thème 2027 inconnu : rien ici ne dépend des missions.

---

## 1. Vue d'ensemble

### 1.1 Arborescence cible

```
aeac-2027/
├── README.md                 quick start en tête, puis tout ce qui aide, rien qui ment (P30)
├── NOTES.md                  journal libre, daté, non organisé (P33)
├── ARCHITECTURE.md           une page : qui tourne où, conventions, section leads (P29)
├── procédure.md              checklist jour J (P28)
├── Makefile                  trois sections : développement, test sur véhicule, déploiement (P5)
├── .gitignore  .dockerignore (P3)
├── .gitmodules               custom_interfaces, tools, nav_stack, vision, zed-ros2-wrapper (P2)
├── compose/
│   ├── dev.yml               poste WSL : image gcs, rviz, rqt, X11 ; dépôt entier monté, on y entre
│   ├── sim.yml               dev + mavros-sim vers SITL ; pas de Zenoh (P25)
│   ├── drone.yml             Jetson : lance la mission de C= ; utilisé par make et par systemd
│   ├── vision.yml            Jetson : conteneur GPU ; idem
│   ├── gcs.yml               portable en vol : nœuds GCS de C= ; pont Zenoh sol
│   └── mavros.yml  zed.yml  zenoh-air.yml  zenoh-ground.yml
├── docker/
│   ├── dockerfile.drone      complet, autonome ; en-tête : « ce qui diffère des autres et pourquoi » (P7)
│   ├── dockerfile.gcs        idem
│   ├── dockerfile.vision     base JetPack, GPU
│   └── dockerfile.mavros
├── config/
│   ├── <mission>.yaml        ce qui change par mission (P19)
│   ├── sites/<site>.yaml     ce qui change par terrain, dont sim.yaml (P20)
│   ├── drones/<drone>.json5  endpoints Zenoh sol par drone (P32)
│   └── mavros.yaml  zenoh-air.json5  zenoh-ground.json5
├── packages/                 paquets partagés
│   ├── custom_interfaces/  tools/  nav_stack/  vision/     [sous-modules]
│   ├── zed-ros2-wrapper/                                    [sous-module tiers, hors workspace]
│   └── sim_mocks/            rc_simulator, target_mock, nœuds *_test (P24)
├── workspaces/               une mission = un workspace (P11)
│   ├── <mission>_ws/src/     symlinks versionnés vers ../../../packages/<pkg> + paquets locaux
│   ├── vision_ws/src/        vision, custom_interfaces, vision_bringup
│   └── gcs_ws/src/           nœuds sol ; c'est aussi le workspace de développement
├── models/                   ignoré par git, rempli par make models (P3)
└── systemd/                  déploiement seulement (P8)
    ├── lo-multicast.service  mavros.service  zed.service  zenoh-air.service  vision.service
    ├── mission.service       lit /etc/aeac/mission, lance compose/drone.yml avec ce C=
    └── install.md
```

Une mission réelle 2027 ajoute `workspaces/<mission>_ws/` (bringup, paquets locaux, symlinks) et `config/<mission>.yaml`. Le Makefile n'a rien à apprendre : `C=<mission>` suffit, comme en 2026 (`WS_REL := workspaces/$(C)_ws`).

### 1.2 Qui tourne où

| Machine | Régime | Ce qui tourne | Lancé par | Domaine |
|---|---|---|---|---|
| Poste WSL | Développement | conteneur `dev` : coder, construire n'importe quel workspace, rviz, `ros2 topic` | `make dev` | 3 |
| Poste WSL | Simulation | conteneur `dev` + `mavros-sim` vers SITL (Mission Planner) ; la mission de `C=` avec `sim:=true` ; mocks à la main | `make sim C=` | 3 |
| Jetson | Test sur véhicule | `mavros`, `zed`, `zenoh-air`, `vision`, mission : les mêmes compose qu'en déploiement, en avant-plan | `make mavros`, `make vision`, `make drone C=` | 2 |
| Jetson | Déploiement | exactement les mêmes compose, au boot, relancés s'ils tombent | systemd | 2 |
| Portable GCS | Vol | conteneur `gcs` (workspace `gcs_ws`, rosbag) + `zenoh-ground` vers le drone choisi | `make gcs C= DRONE=` | 3 |

Règle qui relie les deux lignes Jetson : **tout ce que systemd lance a une cible `make` qui lance la même chose en avant-plan**. systemd est un emballage. Pour tester sur le véhicule, on arrête le service et on lance la cible.

### 1.3 Ce qui traverse la radio

```
Jetson (domaine 2, DDS local seulement)                 Portable (domaine 3, DDS local seulement)
   nœuds mission ──► /aeac/internal/...   (reste ici)
   nœuds mission ──► /aeac/external/...  ──► zenoh-air ══ SIYI ou Tailscale ══ zenoh-ground ──► nœuds GCS
                     /tf, /tf_static     ──►                                                ──►
```

Trois idées, dans cet ordre en formation : le nom du topic dit où il voyage ; DDS ne sort jamais d'une machine ; Zenoh ne porte que ce qui est déclaré externe.

---

## 2. Dépôt et Git

### P1. `main` = ce qui vole
Branche + PR, un lead fusionne. Aucune autre convention enseignée ; `prenom/sujet` suggéré.
- **Effort** : 0 h. **Formation** : Recrue.

### P2. Sous-modules simplifiés, pilotés par le Makefile
Cinq sous-modules dans `packages/`, un paquet ROS par dépôt maison, `package.xml` à la racine du dépôt.

| Cible | Fait | Pour qui |
|---|---|---|
| `make init` | `git submodule update --init` ; pose `submodule.recurse=true` (un `git pull` met les sous-modules à jour tout seul) et `push.recurseSubmodules=on-demand` (git refuse de pousser un pointeur vers un commit non poussé) ; crée `models/`. Idempotent. | Recrue |
| `make status` | Une ligne par sous-module : nom, commit épinglé, `à jour` / `modifié localement` / `en avance sur le pointeur` ; plus la branche courante. La réponse à « qu'est-ce qui se passe avec git ? ». | Recrue |
| `make bump PKG=tools` | Avance le sous-module sur `origin/main`, affiche les commits gagnés, stage le pointeur, pose un tag `aeac-2027-<date>` dans le paquet. | Leads |
| `make check` | Voir P4. | Tous |

Aucun script ne fait `--remote`. Trois phrases enseignées : clone avec `--recurse-submodules` ; `make init` si oublié ; si `make status` dit « modifié localement » sur un paquet partagé, demande à un lead. Le geste complet du lead (`git -C packages/tools switch main`, coder, commit, push, PR, `make bump`) est dans `ARCHITECTURE.md`, section leads.
- **Pourquoi** : brainstorm sections 6.1 à 6.5 ; les cinq causes de la douleur 2026 corrigées une par une. **Effort** : 4 h (cibles + restructuration des quatre dépôts partagés, dont `vision` : double `intialize_topics()`, chargement YOLO en quatre copies). **Formation** : Recrue / Leads.

### P3. `.gitignore` et `.dockerignore`, dépôt sans binaires
`.gitignore` : `build/ install/ log/ __pycache__/ *.pyc models/ *.tlog *.bin *.onnx *.pt *.engine saved_images*/ bags/ .env`. `.dockerignore` : `.git/ models/ **/build/ **/install/ **/log/ bags/ *.png`, pour que `make build` n'envoie plus tout le dépôt au démon Docker (c'est ce qui rendait le premier build lent en 2026). Modèles dans `models/`, `make models` les télécharge depuis un lien écrit dans le Makefile.
- **Effort** : 1 h. **Formation** : Non.

### P4. Métadonnées de paquet remplies, vérifiées par `make check`
Mainteneur réel, licence Apache 2.0, dépendances réelles, pas de dossier `test/`. `make check` parcourt le dépôt et les sous-modules et signale, une ligne par problème : `maintainer` contenant `todo`, licence vide ou `TODO`, description vide, dossier `test/` template, symlink cassé dans un `src/`, sous-module non initialisé, commande `make <cible>` citée dans le README qui n'existe pas dans le Makefile. Script Python de 80 lignes dans `tools/scripts/`.
- **Effort** : 2 h. **Formation** : Recrue (« lance `make check` avant ta PR »).

---

## 3. Infrastructure d'exécution

### P5. Makefile en trois sections
`C=<mission>` reste le sélecteur de compose et de workspace. Toutes les cibles ont un `##` ; `make help` les affiche par section.

**Section 1, développement et simulation (poste WSL)** : `help`, `print-vars`, `init`, `status`, `check`, `models`, `build C=`, `dev` (entre dans le conteneur de dev), `sim C=`, `shell C=`, `logs C=`, `link C= PKG=`, `bag`.
**Section 2, test sur véhicule (Jetson ou portable, à la main, avant-plan)** : `mavros`, `zed`, `zenoh-air`, `vision`, `drone C=`, `gcs C= DRONE=`. Chacune lance le compose correspondant en avant-plan, logs à l'écran, `Ctrl-C` pour arrêter. Ce sont les compose que systemd lance.
**Section 3, déploiement (Jetson, systemd)** : `deploy` (installe les unités depuis `systemd/`, écrit `/etc/aeac/mission`), `<service>-status|logs|restart` pour `mavros`, `zed`, `zenoh`, `vision`, `mission`, `undeploy`.
La section 3 peut n'être écrite qu'au premier déploiement ; les sections 1 et 2 sont dans le template dès le début.
- **Pourquoi** : 51 cibles dont 17 documentées en 2026, fantômes, `DOMAIN` mort (revue 3.2) ; consigne de Colin sur les phases. **Effort** : 4 h. **Formation** : Recrue (sections 1 et 2) ; Leads (section 3, `bump`).

### P6. Compose : un seul montage, la commande est le launch
**Décidé (exploration workspaces, W1).** Tous les compose montent le dépôt entier dans `/aeac`, comme `dev.yml` le fait depuis 2025 et sans coût (un bind-mount ne copie rien), et mettent `working_dir: /aeac/workspaces/$(C)_ws`. Plus de bind-mount paquet par paquet : les symlinks des workspaces résolvent puisque `packages/` est là. La commande des conteneurs de mission est `ros2 launch <mission>_bringup mission.launch.py` (pattern de la branche 2026), ce qui sert à `make drone C=` en avant-plan comme à systemd ; `make shell C=` ouvre un second shell pour déboguer. `dev.yml` garde la boucle d'attente, on y entre. `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` et `ROS_LOCALHOST_ONLY=1` partout où Zenoh fait le pont. Plus de services commentés.
- **Effort** : 2 h. **Formation** : Recrue (lire `sim.yml` et `drone.yml` côte à côte).

### P7. Un Dockerfile complet par rôle, dépendances Python en ligne
**Décidé (exploration dockerfiles, D1 + R1).** Quatre fichiers autonomes, comme en 2026 : `dockerfile.drone`, `dockerfile.gcs`, `dockerfile.vision` (base JetPack, ne se construit que sur la Jetson), `dockerfile.mavros`. `drone` et `gcs` sont presque identiques et c'est assumé. Les dépendances Python sont dans des `RUN pip install` en ligne, comme en 2026, sans fichier requirements ; `requirements_v1.txt` n'est pas repris puisque rien ne le lisait. Trois garde-fous qui ne coûtent rien : l'en-tête de chaque fichier dit en trois lignes ce qui diffère des autres et pourquoi ; la même version de `numpy` partout, chaque épinglage commenté sur sa ligne ; `make check` signale un fichier de `docker/` que personne ne lit. `Dockerfile.vision_test` n'est pas repris.
- **Pourquoi** : « simple à comprendre et à implémenter, et similaire à 2026 qui marchait bien ». La divergence `numpy` de 2026 se règle par la relecture, pas par un mécanisme. **Effort** : 2 h. **Formation** : Recrue (formation 2 couvre Docker ; ici, lire l'en-tête des quatre fichiers). Le contenu de `dockerfile.vision` va au bloc B8.

### P8. systemd : déploiement seulement, jamais la seule voie
Unités de la branche reprises (`lo-multicast`, `mavros`, `zed`, `zenoh-air`, `vision`) plus un `mission.service` unique qui lit `/etc/aeac/mission` et lance `compose/drone.yml` avec ce `C=`. Chaque unité fait `docker compose up` en avant-plan, exactement ce que `make <x>` fait. Pour tester : `make undeploy` puis `make drone C=`. Sur le poste WSL, systemd n'existe pas et n'est jamais nécessaire.
- **Effort** : 1,5 h. **Formation** : Recrue (`-status|logs|restart`, « systemd est un emballage ») ; Leads (installation).

### P9. Domaines ROS et Zenoh, expliqués
2 sur le drone, 3 au sol ; Zenoh `router` des deux côtés, scouting désactivé, `ros_localhost_only: true`, `ROS_LOCALHOST_ONLY=1`, `lo-multicast` ; `allow` limité à `/aeac/external.*`, `/tf`, `/tf_static`. Config de la branche, pas de `main`. Six lignes dans `ARCHITECTURE.md`.
- **Effort** : 1,5 h, dont le test de `make sim` avec `ROS_LOCALHOST_ONLY=1` sous WSL. **Formation** : Recrue.

### P10. Root dans les conteneurs, pour l'instant
`UID`/`GID` retirés du Makefile. **Effort** : 0,5 h. **Formation** : Non.

---

## 4. Workspaces et paquets

**Décidé (exploration workspaces, W1).** Le temps de build compte : chaque mission construit son workspace et rien d'autre, comme en 2026. Ce qui change par rapport à 2026 : une seule liste (les symlinks dans git) au lieu de trois.

### P11. Une mission = un workspace, symlinks versionnés
`workspaces/<mission>_ws/src/` contient les paquets locaux (dossiers) et des symlinks relatifs `../../../packages/<pkg>` vers les partagés, **commis dans git** (la branche 2026 le fait déjà, mode `120000`). `pkgs.txt` et `link_ws.sh` disparaissent. `make build C=water` = `colcon build` dans `water_ws`, sans option ; chaque workspace a ses `build/` et `install/`. `vision_ws` (vision, custom_interfaces, vision_bringup) et `gcs_ws` suivent la même règle. `gcs_ws` est aussi le workspace de développement : pas de `dev_ws`, mais le conteneur `dev` monte le dépôt entier, donc depuis `make dev` on construit et lance n'importe quel workspace (`cd /aeac/workspaces/water_ws && colcon build`). Pas de workspace `sim` : la simulation d'une mission se fait dans le workspace de cette mission.
- **Pièges nommés** : dépôt cloné sous WSL, jamais sous Windows (symlinks) ; un symlink cassé donne un dossier vide que colcon ignore en silence, `make check` le détecte. **Effort** : 1 h. **Formation** : Recrue (jalon : `ls -l src/` dit ce que la mission utilise et ce qui est partagé).

### P12. Ajouter un paquet à une mission
Paquet local : `ros2 pkg create` dans `src/`, commit. Paquet partagé : `make link C=water PKG=polar_system` (un `ln -s` relatif), commit du lien. Rien à éditer dans un compose ni dans une liste.
- **Effort** : 0,5 h. **Formation** : Recrue (jalon : lier `polar_system` et le voir construit).

### P13. `package.xml` est le contrat
Toute dépendance déclarée dans le `package.xml`. Le Dockerfile installe ce que `rosdep` ne couvre pas et le dit en commentaire. Un paquet qui ne se construit pas dans une image fraîche est un bug du paquet.
- **Effort** : 0,5 h. **Formation** : Recrue.

### P14. Règle local / partagé
Un paquet est local (`src/` de sa mission) par défaut. S'il sert à deux workspaces du même dépôt, il va dans `packages/` comme dossier simple (`sim_mocks` en est l'exemple). S'il sert à deux dépôts, il devient sous-module, décision de lead.
- **Effort** : 0 h. **Formation** : Recrue (la phrase) ; Leads (le geste).

---

## 5. Interfaces et nommage

### P15. `tools/tools/topics.py`
Table plate de constantes, deux groupes (externe, interne). Aucun nom de topic en littéral ailleurs. **Effort** : 1 h. **Formation** : Recrue.

### P16. Préfixe unique `/aeac/internal|external/`
Le deuxième segment décide seul de ce qui traverse la radio. **Effort** : 0,5 h. **Formation** : Recrue.

### P17. Enums et constantes dans `custom_interfaces`
États, modes, PWM : constantes de message, jamais redéfinies dans un nœud. **Effort** : 1 h. **Formation** : Recrue.

### P18. Règle de langue
Code, topics, commentaires, commits en anglais ; docs, docstrings de haut niveau, logs en français. **Effort** : 0 h. **Formation** : Recrue.

---

## 6. Configuration par mission, par site, par drone

### P19. `config/<mission>.yaml`
Gains, PWM, mapping RC, coordonnées de scène, chemins, seuils. Pas de dict inline dans les launch. **Effort** : 1,5 h. **Formation** : Recrue.

### P20. `config/sites/<site>.yaml`
Coordonnées et altitudes par terrain, `site:=compétition` au launch, fusionné par-dessus le YAML de mission. `sim.yaml` pour la simulation. **Effort** : 1 h. **Formation** : Recrue.

### P32. `config/drones/<drone>.json5`
Endpoints Zenoh sol (SIYI et Tailscale) par drone, `make gcs DRONE=hexa`. Tableau d'adressage dans `ARCHITECTURE.md`. **Effort** : 1 h. **Formation** : Recrue / Leads.

---

## 7. Sécurité de vol dans le code

### P21. Le code de mission n'arme jamais, sauf les nœuds de test sous `sim`
Un nœud qui appelle `arming` ou `set_mode` porte le suffixe `_test`, vit dans `sim_mocks`, déclare le paramètre `sim` et refuse de démarrer s'il n'est pas vrai, et n'est jamais inclus par un launch de mission. La node `takeoff` de la formation 3.4 est le modèle.
- **Effort** : 0,5 h. **Formation** : Recrue.

### P22. Pas de vérification factice, pas de sommeil dans un callback
Deux interdits nommés. `nav_stack/init` corrigé avant d'entrer dans le template. **Effort** : 2 h. **Formation** : Recrue.

### P23. Heartbeat avec comportement défini
`gcs_heartbeat` et son pendant drone ; délai et action dans le YAML ; topic `/aeac/internal/link_ok`. **Effort** : 1 h. **Formation** : Recrue.

---

## 8. La mission en simulation

### P24. `packages/sim_mocks/`
`rc_simulator` (clavier vers `/mavros/rc/in`), `target_mock` (détection fixe ou mobile), nœuds `*_test` (P21). README qui liste chaque mock, ce qu'il remplace, le topic qu'il publie. **Effort** : 2 h. **Formation** : Recrue.

### P25. `make sim C=<mission>`, version minimale
**Décidé (exploration simulation, réduit).** SITL externe dans Mission Planner sous Windows reste la référence (Gazebo, formation 4, reste possible). `make sim C=water` fait deux choses : lance `sim.yml` (conteneur `dev` + `mavros-sim` vers `tcp://<IP Windows>:5762`, comme `make mavros-sim` en formation 3) puis `ros2 launch water_bringup mission.launch.py sim:=true site:=sim` en avant-plan. `sim:=true` ne fait qu'une chose : passer le paramètre `sim` aux nœuds. Un nœud qui touche au matériel lit `sim` une fois et entoure son seul appel matériel d'un `if not self.sim:` ; les autres nœuds n'ont pas le paramètre. Les mocks se lancent à la main dans un second terminal (`make shell C=water`, puis `ros2 run sim_mocks rc_simulator`), parce que `rc_simulator` lit le clavier et parce qu'on garde ça simple, comme en 2026. Pas de launch de mocks, pas d'inclusion automatique.
- **Effort** : 2 h. **Formation** : Recrue (cœur de la formation 5 : trois terminaux, la mission qui passe par ses états dans `ros2 topic echo`).

### P26. La mission démo vit dans la formation 5
**Décidé (exploration simulation, M2).** Le template ne contient aucune mission. La formation 5 fournit `demo_ws/` (quatre états `IDLE`, `GOTO`, `ACT`, `RETURN`, un GO externe, un waypoint du YAML, une action factice, retour ; états en constantes de `custom_interfaces`, `_transition()` unique et loggé, paramètre `sim`, topics de `topics.py` ; une centaine de lignes) et guide la recrue : copier `mission-template/`, déposer `demo_ws` dans `workspaces/`, `make link` des partagés, `make sim C=demo`. aeac-2027 ne voit jamais la démo.
- **Effort** : 4 h, imputées à la formation 5. **Formation** : Recrue.

---

## 9. Observabilité terrain

### P27. Règle de logs
`INFO` pour les événements, jamais pour du périodique ; `WARN` demande un regard ; `ERROR` arrête. En français. **Effort** : 0,5 h. **Formation** : Recrue.

### P28. `make bag` et `procédure.md`
Enregistrement daté des topics `/aeac/*` et `/mavros/*` utiles ; `procédure.md` repris de 2026 avec les noms 2027 et « `make bag` avant le décollage ». **Effort** : 1 h. **Formation** : Recrue.

---

## 10. Documentation

### P29. `ARCHITECTURE.md`, une page
Tableau qui-tourne-où (1.2), schéma radio (1.3), règles (mission = workspace + YAML, langue, logs, sous-modules en trois phrases, systemd est un emballage), tableau d'adressage, section leads. **Effort** : 2 h. **Formation** : Recrue.

### P30. README : quick start en tête, puis tout ce qui aide, rien qui ment
Quick start en quinze lignes, puis des sections libres (dépannage Jetson, UART JetPack 5 et 6, réseau, astuces) tant qu'elles sont vraies. `make check` vérifie que chaque `make <cible>` cité existe. Le guide WSL reste dans les formations. **Effort** : 1 h. **Formation** : Recrue.

### P33. `NOTES.md`, le journal non organisé
Une date, un nom, le texte. Aucune structure, aucune relecture exigée, jamais de ménage sans l'accord de l'auteur. Le successeur assumé de « Notes pas organisées », nommé pour ce qu'il est. Un lead promeut de temps en temps ce qui le mérite vers le README ou `ARCHITECTURE.md`. **Effort** : 0 h. **Formation** : Recrue.

### P31. Un README de cinq lignes par paquet
Rôle, nœuds, topics (par leurs noms dans `topics.py`), paramètres. **Effort** : 1 h. **Formation** : Recrue.

---

## 11. Hors du template : ce que 2027 portera au besoin

Inchangé : `polar_system`, `gimbal_controller`, `remote_controller_interface`, `shoot_and_capture`, contrôleurs de charge utile, serveurs web C++, `control_nav`, avec le nettoyage listé dans la revue (sections 3.4 et 3.5). `TerminationSystem` n'est pas porté. `vision` est un sous-module du template (P2).

---

## 12. Parallèle 2026 / 2027 pour la formation

| Sujet | aeac-2026 (branche de compétition) | aeac-2027 |
|---|---|---|
| Branche par défaut | `main` mort, code de compétition sur une branche | `main` = ce qui vole (P1) |
| Sous-modules | 8, script `--remote`, nesting à trois niveaux | 5, `make init` / `status` / `bump`, un paquet par dépôt (P2) |
| Workspaces | Un par mission, trois listes (symlinks git, `pkgs.txt`, bind-mounts) | Un par mission, une liste : les symlinks dans git (P11) |
| Ajouter un paquet | `pkgs.txt` + `link_ws.sh` + compose | `make link` + commit (P12) |
| Montage des conteneurs | Le workspace seul + un bind-mount par paquet | Le dépôt entier, `working_dir` sur le workspace (P6) |
| Dev, test, déploiement | Mélangés dans 51 cibles | Trois sections nommées ; systemd = emballage (P5, P8) |
| Dockerfiles | Nommés par mission, `numpy` divergent, `pip freeze` mort | Nommés par rôle, en-tête « ce qui diffère », même `numpy` (P7) |
| Noms de topics | Quatre familles, quatre câblages morts | `topics.py`, préfixe unique (P15, P16) |
| Enums, PWM | Redéfinis dans trois fichiers | Constantes de `custom_interfaces` (P17) |
| Gains, coordonnées, endpoints | Copiés dans les launch et les json5 | YAML par mission, par site, json5 par drone (P19, P20, P32) |
| Tourner sans drone | Mocks éparpillés, mode `sim` dans un nœud | `sim_mocks`, paramètre `sim` partout où il faut, `make sim`, démo dans la formation (P24 à P26) |
| Zenoh | `router` sans scouting sur la branche, `peer` sur `main` | `router`, `ROS_LOCALHOST_ONLY=1`, `lo-multicast` (P9) |
| Doc | README de 270 lignes avec « Notes pas organisées » | README vrai + `NOTES.md` + `ARCHITECTURE.md` (P29, P30, P33) |
| Sécurité | Readiness stubs, `TerminationSystem` mort | Vérifications réelles ou absentes, `_test` sous `sim` seulement (P21, P22) |
| Repris tels quels | Réseau, domaines, systemd, `procédure.md`, `gcs_heartbeat`, forme d'`auto_approach`, Dockerfiles par rôle, pip en ligne | (P7, P8, P9, P23, P28) |

---

## 13. Récapitulatif

| # | Proposition | Effort | Formation |
|---|---|---|---|
| P1 | `main` = ce qui vole | 0 h | Recrue |
| P2 | Sous-modules simplifiés, `make init/status/bump` | 4 h | Recrue / Leads |
| P3 | `.gitignore`, `.dockerignore`, modèles hors git | 1 h | Non |
| P4 | Métadonnées + `make check` | 2 h | Recrue |
| P5 | Makefile en trois sections | 4 h | Recrue / Leads |
| P6 | Compose : un montage, la commande est le launch | 2 h | Recrue |
| P7 | Un Dockerfile complet par rôle, pip en ligne | 2 h | Recrue |
| P8 | systemd : déploiement seulement | 1,5 h | Recrue / Leads |
| P9 | Zenoh router, domaines expliqués | 1,5 h | Recrue |
| P10 | Root dans les conteneurs | 0,5 h | Non |
| P11 | Une mission = un workspace, symlinks git | 1 h | Recrue |
| P12 | `make link` | 0,5 h | Recrue |
| P13 | `package.xml` est le contrat | 0,5 h | Recrue |
| P14 | Règle local / partagé | 0 h | Recrue / Leads |
| P15 | `topics.py` | 1 h | Recrue |
| P16 | Préfixe unique | 0,5 h | Recrue |
| P17 | Enums dans `custom_interfaces` | 1 h | Recrue |
| P18 | Règle de langue | 0 h | Recrue |
| P19 | YAML par mission | 1,5 h | Recrue |
| P20 | YAML par site | 1 h | Recrue |
| P32 | json5 par drone | 1 h | Recrue / Leads |
| P21 | Le code n'arme jamais, sauf `_test` sous `sim` | 0,5 h | Recrue |
| P22 | Pas de stub, pas de sleep | 2 h | Recrue |
| P23 | Heartbeat défini | 1 h | Recrue |
| P24 | `sim_mocks` | 2 h | Recrue |
| P25 | `make sim`, version minimale | 2 h | Recrue |
| P26 | Démo dans la formation 5 | 4 h (formation) | Recrue |
| P27 | Règle de logs | 0,5 h | Recrue |
| P28 | `make bag`, `procédure.md` | 1 h | Recrue |
| P29 | `ARCHITECTURE.md` | 2 h | Recrue / Leads |
| P30 | README vrai, quick start en tête | 1 h | Recrue |
| P33 | `NOTES.md` journal | 0 h | Recrue |
| P31 | README par paquet | 1 h | Recrue |
| | **Total template et dépôts partagés** | **~41 h** | |
| | **Plus la démo, côté formation** | **4 h** | |

Tout est décidé. Aucune proposition n'est en attente.

---

## 14. Ordre de réalisation

1. **Dépôts partagés** (P2, P4, P22) : restructurer `custom_interfaces`, `tools`, `nav_stack`, `vision` sur `main` (un paquet à la racine, code mort retiré, `init` corrigé) ; `topics.py`, constantes d'enum ; `make check`. Prérequis de tout le reste.
2. **Squelette** (P3, P5 sections 1 et 2, P6, P7, P9 à P14) : Makefile, compose, quatre Dockerfiles, `gcs_ws` et `vision_ws`, `.gitignore`, `.dockerignore`. Jalon : `make build C=gcs` passe dans une image fraîche sous WSL, `make dev` donne un shell.
3. **Simulation** (P19, P20, P21, P24, P25) : mocks, YAML, `sim.yml`, `make sim`. Jalon : `make sim C=gcs` lance mavros vers SITL sans erreur, `ros2 run sim_mocks rc_simulator` publie sur `/mavros/rc/in`.
4. **Documentation** (P18, P27 à P31, P33) : `ARCHITECTURE.md`, README, `NOTES.md`, `procédure.md`, README de paquets. Jalon : une recrue fait `make sim` en suivant seulement le README.
5. **Déploiement** (P5 section 3, P8, P32) : au premier passage sur une Jetson 2027.
6. **aeac-2027** : copie du template, `git init`, `git submodule add` des cinq sous-modules, premier commit.
7. **Formation 5** : `demo_ws` (P26), rédaction sur le template, fil de la revue section 6, section 12 comme avant / après.

---

## 15. Commentaires de Colin sur la V2 (21 septembre 2026) et traitement

| Sujet | Commentaire | Traitement dans la V3 |
|---|---|---|
| Partage de code | C. | Confirmé, P2. |
| Dockerfiles, Q1 | D1, un Dockerfile complet par rôle. | P7 réécrit. |
| Dockerfiles, Q2 | R1, pip en ligne comme 2026, plus simple pour les nouveaux et ça marche. | P7 : pas de requirements ; garde-fous sans mécanisme (en-tête, même `numpy`, `make check`). |
| Principe | Options simples à comprendre et implémenter, similaires à 2026 qui marchait bien. | Repris comme fil directeur en tête du document. |
| `make sim` | Utile, mais barebones : juste un paramètre pour influencer les nœuds, comme 2026. | P25 réduit : `sim:=true` ne fait que passer le paramètre ; mocks lancés à la main ; pas de launch de mocks. |
| SITL | Externe, référence. | P25. |
| Nœuds de test qui arment | Autorisés, idéalement sous un paramètre `sim`. | P21 : suffixe `_test`, paramètre `sim` obligatoire. |
| Démo | M2, dans la formation 5. | P26. |
| `rc_simulator` en avant-plan | Ça marche, il faut ce qu'il faut. | P25 : `make sim` et les mocks en avant-plan. |
| Workspaces | Le temps de build est important ; W1. | P6, P11 à P14 décidés selon W1. |
| `dev_ws` | Plutôt `gcs_ws` seulement, comme 2026 ; mais les lancements de dev voient tous les workspaces. | P11 : pas de `dev_ws` ; `gcs_ws` est le workspace de dev ; `dev.yml` monte le dépôt entier, on construit et lance n'importe quel workspace depuis `make dev`. |
| Workspace `sim` | Pas de workspace à part. | P11. |
