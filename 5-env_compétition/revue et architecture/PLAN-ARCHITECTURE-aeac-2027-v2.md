# Plan d'architecture aeac-2027, version 2

*21 septembre 2026, après la revue de la V1 par Colin (commentaires reportés en section 15). Ce document a deux usages : plan du dépôt `aeac-2027` (et du dossier `mission-template/` dont il sera la copie), et fil de la future Formation 5. Il part de la branche de compétition d'aeac-2026 (`mission-2-photo-pipeline`, `71408c4`) et de sa revue pédagogique. Les points encore ouverts renvoient à trois documents d'exploration du même dossier : `EXPLORATION-workspaces-et-builds.md`, `EXPLORATION-dockerfiles-et-requirements.md`, `EXPLORATION-simulation-et-mission-demo.md`. La V3 intégrera les réponses.*

**Comment lire.** Chaque `P<n>` donne ce qu'on fait, pourquoi, l'effort, et la ligne **Formation** : *Recrue*, *Leads* ou *Non*. Le **Statut** dit où en est la décision : *Accepté* (V1 validée), *Accepté, précisé* (V1 validée avec une consigne intégrée ici), *En exploration* (document à discuter). La numérotation de la V1 est conservée pour le suivi ; P33 est nouvelle.

**Décisions prises à ce jour** : squelette générique seulement dans le template ; code en anglais, docs et logs en français ; template dans `Control-Formations/5-env_compétition/mission-template/` ; sous-modules simplifiés, cinq au total (`custom_interfaces`, `tools`, `nav_stack`, `vision`, `zed-ros2-wrapper`) ; dépôts partagés repris et restructurés ; SUAS 2027 dans un dépôt séparé ; le dépôt garde le nom `aeac-2027` ; `main` = ce qui vole ; pas de tests ; root dans les conteneurs à court terme ; **deux régimes distincts dans le Makefile : développement et test d'un côté, déploiement sur véhicule de l'autre**.

**Hypothèses.** Même matériel qu'en 2026 (Jetson Orin, ZED, SIYI HM30, LTE + Tailscale, portable GCS sous WSL, deux drones). Thème 2027 inconnu : rien ici ne dépend des missions.

---

## 1. Vue d'ensemble

### 1.1 Arborescence cible

Les points marqués `(?)` dépendent d'une exploration en cours.

```
aeac-2027/
├── README.md                 quick start, puis tout ce qui aide (P30)
├── NOTES.md                  journal libre, non organisé, daté (P33)
├── ARCHITECTURE.md           une page : tableau qui-tourne-où, conventions, section leads (P29)
├── procédure.md              checklist jour J (P28)
├── Makefile                  trois sections : développement, test sur véhicule, déploiement (P5)
├── .gitignore  .dockerignore (P3)
├── .gitmodules               custom_interfaces, tools, nav_stack, vision, zed-ros2-wrapper (P2)
├── compose/
│   ├── dev.yml               poste WSL : image gcs, rviz, rqt, X11 ; pour coder et simuler
│   ├── sim.yml               dev + mavros-sim vers SITL ; pas de Zenoh (P25)
│   ├── drone.yml             Jetson : lance la mission de C= ; utilisé par make ET par systemd
│   ├── vision.yml            Jetson : conteneur GPU ; idem
│   ├── gcs.yml               portable en vol : nœuds GCS de C=, pont Zenoh sol
│   ├── mavros.yml  zed.yml  zenoh-air.yml  zenoh-ground.yml
├── docker/                   (?) voir EXPLORATION-dockerfiles : dockerfile.ros multi-étapes + dockerfile.vision,
│                             ou un Dockerfile par rôle ; requirements-<rôle>.txt lus par les builds (P7)
├── config/
│   ├── <mission>.yaml        ce qui change par mission (P19)
│   ├── sites/<site>.yaml     ce qui change par terrain (P20)
│   ├── drones/<drone>.json5  endpoints Zenoh sol par drone (P32)
│   ├── mavros.yaml  zenoh-air.json5  zenoh-ground.json5
├── packages/                 paquets partagés : sous-modules, plus dossiers simples partagés entre workspaces
│   ├── custom_interfaces/  tools/  nav_stack/  vision/     [sous-modules]
│   ├── zed-ros2-wrapper/                                    [sous-module tiers, hors workspace]
│   └── sim_mocks/            rc_simulator, target_mock, nœuds *_test (P24)
├── workspaces/               (?) voir EXPLORATION-workspaces : une mission = un workspace,
│   ├── <mission>_ws/src/     symlinks versionnés vers packages/ + paquets locaux (P11, P12)
│   ├── vision_ws/src/
│   └── gcs_ws/src/
├── models/                   ignoré par git, rempli par make models (P3)
└── systemd/                  déploiement seulement : lo-multicast, mavros, zed, zenoh-air, vision, mission (P8)
```

Une mission réelle 2027 ajoute : `workspaces/<mission>_ws/` (bringup + paquets locaux + symlinks), `config/<mission>.yaml`. Le Makefile n'a rien à apprendre : `C=<mission>` suffit.

### 1.2 Qui tourne où

Remplace les schémas ASCII de la V1, jugés peu lisibles.

| Machine | Régime | Ce qui tourne | Lancé par | Domaine ROS |
|---|---|---|---|---|
| Poste WSL | Développement | conteneur `dev` (coder, rviz, `ros2 topic`) | `make dev` | 3 |
| Poste WSL | Simulation | conteneur `dev` + `mavros-sim` vers SITL (Mission Planner) + mocks + mission | `make sim C=` | 3 |
| Jetson | Test sur véhicule | `mavros`, `zed`, `zenoh-air`, `vision`, mission : les mêmes compose qu'en déploiement, en avant-plan | `make mavros`, `make vision`, `make drone C=` | 2 |
| Jetson | Déploiement | exactement les mêmes compose, démarrés au boot et relancés s'ils tombent | systemd | 2 |
| Portable GCS | Vol | conteneur `gcs` (nœuds sol, rosbag) + `zenoh-ground` vers le drone choisi | `make gcs C= DRONE=` | 3 |

Règle qui relie les deux dernières lignes Jetson : **tout ce que systemd lance a une cible `make` qui lance la même chose en avant-plan**. systemd est un emballage, jamais la seule façon de lancer quelque chose. Pour tester sur le véhicule, on arrête le service et on lance la cible.

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
*Statut : Accepté.* Un seul rôle pour `main`. Branche + PR, un lead fusionne. Aucune autre convention enseignée ; `prenom/sujet` suggéré.
- **Effort** : 0 h. **Formation** : Recrue.

### P2. Sous-modules simplifiés, pilotés par le Makefile
*Statut : Accepté, précisé.* Cinq sous-modules dans `packages/`, un paquet ROS par dépôt maison, `package.xml` à la racine. Consigne de Colin intégrée : le suivi des sous-modules passe par des cibles Make, pas par des commandes git à retenir.

| Cible | Fait | Pour qui |
|---|---|---|
| `make init` | `git submodule update --init`, pose `submodule.recurse=true` et `push.recurseSubmodules=on-demand`, crée `models/`. Idempotent, à relancer sans risque. | Recrue |
| `make status` | Une ligne par sous-module : nom, commit épinglé, `à jour` / `modifié localement` / `en avance sur le pointeur`, plus la branche du superprojet. La réponse à « qu'est-ce qui se passe avec git ? ». | Recrue |
| `make bump PKG=tools` | Avance le sous-module sur `origin/main`, affiche les commits gagnés, stage le pointeur, pose un tag `aeac-2027-<date>` dans le paquet. | Leads |
| `make check` | Voir P4. | Tous |

Aucun script ne fait `--remote`. Trois phrases enseignées : clone avec `--recurse-submodules` ; `make init` si oublié ; si `make status` dit « modifié localement » sur un paquet partagé, demande à un lead.
- **Pourquoi** : brainstorm sections 6.1 à 6.5. **Effort** : 4 h (cibles + restructuration des quatre dépôts partagés, dont la correction de `vision` : double `intialize_topics()`, chargement YOLO en quatre copies). **Formation** : Recrue (les trois phrases, `make status`) ; Leads (`make bump`, brainstorm 6.3).

### P3. `.gitignore` et `.dockerignore` complets, dépôt sans binaires
*Statut : Accepté.* `.gitignore` : `build/ install/ log/ __pycache__/ *.pyc models/ *.tlog *.bin *.onnx *.pt *.engine saved_images*/ bags/ .env`. `.dockerignore` (nouveau, issu de l'exploration workspaces) : `.git/ models/ **/build/ **/install/ **/log/ bags/ *.png`, pour que `make build` n'envoie plus tout le dépôt au démon Docker. Modèles dans `models/`, remplis par `make models`.
- **Effort** : 1 h. **Formation** : Non.

### P4. Métadonnées de paquet remplies, vérifiées par `make check`
*Statut : Accepté, précisé.* Mainteneur réel, licence Apache 2.0, dépendances réelles, pas de dossier `test/`. Consigne de Colin intégrée : `make check` vérifie et dit ce qui manque. Il parcourt tous les `package.xml` du dépôt et des sous-modules et signale : `maintainer` contenant `todo`, `license` vide ou `TODO`, `description` vide, dossier `test/` template (md5 des trois fichiers de `ros2 pkg create`), symlink cassé dans un `src/`, sous-module non initialisé, fichier dans `docker/` qui n'est lu par aucun Dockerfile. Sortie : une ligne par problème, code de retour non nul. Un script Python de 80 lignes dans `tools/scripts/`.
- **Effort** : 2 h. **Formation** : Recrue (« lance `make check` avant ta PR »).

---

## 3. Infrastructure d'exécution

### P5. Makefile en trois sections : développement, test sur véhicule, déploiement
*Statut : Accepté, précisé.* Consigne de Colin intégrée : le Makefile distingue explicitement les phases, et le déploiement n'est jamais la seule façon de lancer quelque chose. `C=<mission>` reste le sélecteur. Toutes les cibles ont un `##` ; `make help` les affiche groupées par section.

**Section 1, développement et simulation (poste WSL)** : `help`, `print-vars`, `init`, `status`, `check`, `models`, `build C=`, `dev` (conteneur de dev, shell), `sim C=` (simulation complète, avant-plan), `shell C=`, `logs C=`, `link C= PKG=`, `bag`.
**Section 2, test sur véhicule (Jetson ou portable, à la main, en avant-plan)** : `mavros`, `zed`, `zenoh-air`, `vision`, `drone C=`, `gcs C= DRONE=`. Chacune lance le compose correspondant en avant-plan, logs à l'écran, `Ctrl-C` pour arrêter. Ce sont exactement les compose que systemd lance.
**Section 3, déploiement (Jetson, systemd)** : `deploy` (installe ou met à jour les unités systemd depuis `systemd/` et écrit `/etc/aeac/mission`), `<service>-status|logs|restart` pour `mavros`, `zed`, `zenoh`, `vision`, `mission`, et `undeploy` (arrête et désactive tout, pour repasser en test à la main).
**Leads** : `bump`, `deploy`, `undeploy`.

Ce qui n'est pas obligatoire au départ : la section 3 peut n'exister que sur la Jetson et n'être écrite qu'au premier déploiement ; les sections 1 et 2 sont dans le template dès le début.
- **Pourquoi** : 51 cibles dont 17 documentées en 2026, cibles fantômes, `DOMAIN` mort (revue 3.2) ; et la consigne que dev, test et déploiement soient trois choses nommées. **Effort** : 4 h. **Formation** : Recrue (sections 1 et 2) ; Leads (section 3).

### P6. Compose : un seul mécanisme de montage, la commande est le launch
*Statut : En exploration (EXPLORATION-workspaces, section 5).* Proposition issue de l'exploration : tous les compose montent le dépôt entier dans `/aeac` (comme `dev.yml` le fait déjà depuis 2025, et sans coût : un bind-mount ne copie rien) et mettent `working_dir` sur le workspace de `C`. Plus de bind-mount paquet par paquet. La commande des conteneurs de mission est `ros2 launch <mission>_bringup mission.launch.py` (pattern de la branche), ce qui sert autant à `make drone C=` en avant-plan qu'à systemd ; `make shell C=` ouvre un second shell pour déboguer. `dev.yml` garde la boucle d'attente puisque c'est un conteneur où l'on entre. `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` et `ROS_LOCALHOST_ONLY=1` partout où Zenoh fait le pont.
- **Effort** : 2 h. **Formation** : Recrue (lire `sim.yml` et `drone.yml` côte à côte).

### P7. Images Docker et dépendances Python
*Statut : En exploration (EXPLORATION-dockerfiles).* Ce que la V1 voulait dire : un `requirements.txt` est lu par un Dockerfile ou n'existe pas ; `requirements_v1.txt` de 2026 (206 lignes de `pip freeze`, lu par personne) est le cas à éviter. Proposition issue de l'exploration : `docker/dockerfile.ros` multi-étapes (`base`, `mavros`, `drone`, `gcs`) et `docker/dockerfile.vision` séparé sur base JetPack, avec un `requirements-<rôle>.txt` par image, copié et installé par le build. Repli si les étapes nommées sont une notion de trop : un Dockerfile par rôle, mais avec les mêmes `requirements-*.txt`. Dans les deux cas : même `numpy` partout, chaque épinglage commenté, `.dockerignore`.
- **Effort** : 3 h. **Formation** : Recrue (formation 2 couvre Docker ; ici, lire l'étape ou l'en-tête de chaque image). Le contenu de `dockerfile.vision` va au bloc B8.

### P8. systemd : déploiement seulement, et jamais la seule voie
*Statut : Accepté, précisé.* Consigne de Colin intégrée. Les unités de la branche sont reprises (`lo-multicast`, `mavros`, `zed`, `zenoh-air`, `vision`) plus un `mission.service` unique qui lit `/etc/aeac/mission` et lance `compose/drone.yml` avec ce `C=`. Chaque unité fait `docker compose -f compose/<x>.yml up` en avant-plan, exactement ce que `make <x>` fait à la main. Pour tester sur le véhicule : `make undeploy` (ou `systemctl stop mission`), puis `make drone C=` et les logs sont à l'écran. Sur le poste WSL, systemd n'existe pas et n'est jamais nécessaire. `install.md` en dix lignes, remplacé à terme par `make deploy`.
- **Pourquoi** : meilleur élément du dépôt (revue 2) ; la branche a un service par mission avec compose codé en dur, un service paramétré évite d'en créer un par mission. **Effort** : 1,5 h. **Formation** : Recrue (les trois cibles `-status|logs|restart`, et la règle « systemd est un emballage ») ; Leads (installation).

### P9. Domaines ROS et Zenoh, expliqués
*Statut : Accepté.* 2 sur le drone, 3 au sol ; Zenoh en mode `router` des deux côtés, scouting désactivé, `ros_localhost_only: true`, `ROS_LOCALHOST_ONLY=1`, service `lo-multicast` ; listes `allow` limitées à `/aeac/external.*`, `/tf`, `/tf_static`. Config de la branche, pas de `main`. Six lignes dans `ARCHITECTURE.md` (section 1.3 ci-dessus).
- **Effort** : 1,5 h, dont le test que `make sim` fonctionne avec `ROS_LOCALHOST_ONLY=1` sous WSL. **Formation** : Recrue.

### P10. Root dans les conteneurs, pour l'instant
*Statut : Accepté.* `UID`/`GID` retirés du Makefile. **Effort** : 0,5 h. **Formation** : Non.

---

## 4. Workspaces et paquets

*P11 à P14 : En exploration (EXPLORATION-workspaces). La V1 proposait un seul workspace ; Colin préfère une mission = un workspace comme en 2026, pour garder des builds petits et tangibles. L'exploration montre que le coût de build ne dépend que des paquets construits, jamais du montage, et propose de garder les workspaces par mission en supprimant les deux listes redondantes de 2026. Ce qui suit est cette proposition.*

### P11. Une mission = un workspace, symlinks versionnés
`workspaces/<mission>_ws/src/` contient les paquets locaux de la mission (dossiers) et des symlinks relatifs vers `packages/<pkg>` pour les partagés, **commis dans git**, ce que la branche 2026 fait déjà (mode `120000` dans `git ls-tree`). `pkgs.txt` et `link_ws.sh` disparaissent : git porte la liste. `make build C=water` = `colcon build` dans `water_ws`, sans option ; chaque workspace a ses `build/` et `install/`. `vision_ws` et `gcs_ws` suivent la même règle.
- **Effort** : 1 h. **Formation** : Recrue (jalon : `ls -l src/` dit ce que la mission utilise et ce qui est partagé).

### P12. Ajouter un paquet à une mission
Paquet local : `ros2 pkg create` dans `src/`, commit. Paquet partagé : `make link C=water PKG=polar_system` (un `ln -s` relatif), commit du lien. `make check` signale un lien cassé. Rien à éditer dans un compose ni dans une liste.
- **Effort** : 0,5 h. **Formation** : Recrue (jalon : lier `polar_system` à un workspace et le voir construit).

### P13. `package.xml` est le contrat
Toute dépendance est déclarée dans le `package.xml`. Le Dockerfile installe ce que `rosdep` ne couvre pas et le dit en commentaire. Un paquet qui ne se construit pas dans une image fraîche est un bug du paquet.
- **Effort** : 0,5 h. **Formation** : Recrue.

### P14. Règle « local, partagé entre workspaces, partagé entre dépôts »
Un paquet est local (`src/` de sa mission) par défaut. S'il sert à deux workspaces du même dépôt, il va dans `packages/` comme dossier simple. S'il sert à deux dépôts, il devient sous-module, décision de lead. Question ouverte dans l'exploration : garder cette règle à trois niveaux, ou n'avoir que local et sous-module ?
- **Effort** : 0 h. **Formation** : Recrue (la phrase) ; Leads (le geste).

---

## 5. Interfaces et nommage

### P15. `tools/tools/topics.py`
*Statut : Accepté.* Table plate de constantes, deux groupes (externe, interne). Aucun nom de topic en littéral ailleurs. **Effort** : 1 h. **Formation** : Recrue.

### P16. Préfixe unique `/aeac/internal|external/`
*Statut : Accepté.* Le deuxième segment décide seul de ce qui traverse la radio. **Effort** : 0,5 h. **Formation** : Recrue.

### P17. Enums et constantes dans `custom_interfaces`
*Statut : Accepté.* États, modes, PWM : constantes de message, jamais redéfinies dans un nœud. **Effort** : 1 h. **Formation** : Recrue.

### P18. Règle de langue
*Statut : Accepté.* Code, topics, commentaires, commits en anglais ; docs, docstrings de haut niveau, logs en français. **Effort** : 0 h. **Formation** : Recrue.

---

## 6. Configuration par mission, par site, par drone

### P19. `config/<mission>.yaml`
*Statut : Accepté.* Gains, PWM, mapping RC, coordonnées de scène, chemins, seuils. Pas de dict inline dans les launch. **Effort** : 1,5 h. **Formation** : Recrue.

### P20. `config/sites/<site>.yaml`
*Statut : Accepté.* Coordonnées et altitudes par terrain, `site:=compétition` au launch, fusionné par-dessus le YAML de mission. Un `sim.yaml` pour la simulation. **Effort** : 1 h. **Formation** : Recrue.

### P32. `config/drones/<drone>.json5`
*Statut : Accepté.* Endpoints Zenoh sol (SIYI et Tailscale) par drone, `make gcs DRONE=hexa`. Le tableau d'adressage vit dans `ARCHITECTURE.md`. **Effort** : 1 h. **Formation** : Recrue (le tableau) ; Leads (ajouter un drone).

---

## 7. Sécurité de vol dans le code

### P21. Le code de mission n'arme jamais et ne change jamais de mode
*Statut : Accepté, précisé.* Consigne de Colin intégrée : en simulation, des nœuds de test qui arment et décollent sont permis et utiles. Règle complète : un nœud qui appelle `arming` ou `set_mode` porte le suffixe `_test`, vit dans `sim_mocks`, refuse de démarrer si `sim` n'est pas vrai, et n'est jamais inclus par un launch de mission. La node `takeoff` de la formation 3.4 est le modèle.
- **Effort** : 0,5 h. **Formation** : Recrue.

### P22. Pas de vérification factice, pas de sommeil dans un callback
*Statut : Accepté.* Deux interdits nommés (`time.sleep` dans un callback, `spin_until_future_complete` depuis un callback). `nav_stack/init` corrigé avant d'entrer dans le template. **Effort** : 2 h. **Formation** : Recrue.

### P23. Heartbeat avec comportement défini
*Statut : Accepté.* `gcs_heartbeat` et son pendant drone ; délai et action dans le YAML ; topic `/aeac/internal/link_ok`. **Effort** : 1 h. **Formation** : Recrue.

---

## 8. La mission en simulation

### P24. `packages/sim_mocks/`
*Statut : Accepté.* `rc_simulator`, `target_mock`, nœuds `*_test` (P21), un README qui liste chaque mock, ce qu'il remplace et le topic qu'il publie. **Effort** : 2 h. **Formation** : Recrue.

### P25. `make sim C=<mission>` : la mission de bout en bout sans drone
*Statut : En exploration (EXPLORATION-simulation, sections 1 à 3), reformulé.* Ce que ça lance, concrètement : SITL dans Mission Planner sous Windows (formations 1 et 3), `mavros-sim` en TCP 5762 dans le conteneur `dev`, et le launch de la mission, **le même qu'en vol**, avec `sim:=true` et `site:=sim`. `sim:=true` fait deux choses : passer le paramètre `sim` aux nœuds qui touchent au matériel (ils neutralisent leur sortie ou ne changent rien), et inclure `sim_mocks/launch/mocks.launch.py` qui publie sur les topics matériels (RC, détections). Pas de launch « sim » séparé, donc rien qui puisse diverger du vrai. En avant-plan, parce que `rc_simulator` lit le clavier.
- **Effort** : 3 h. **Formation** : Recrue (cœur de la formation 5).

### P26. La mission démo vit dans la formation 5, pas dans le template
*Statut : En exploration (EXPLORATION-simulation, sections 4 à 6), réorienté selon la réserve de Colin.* Le template ne contient aucune mission. La formation 5 fournit `demo_ws/` (quatre états, un GO externe, un waypoint du YAML, une action factice, retour ; une centaine de lignes) et guide la recrue pour le déposer dans une copie du template, lier les paquets partagés et lancer `make sim C=demo`. aeac-2027 ne voit jamais la démo.
- **Effort** : 4 h, imputées à la formation 5. **Formation** : Recrue.

---

## 9. Observabilité terrain

### P27. Règle de logs
*Statut : Accepté.* `INFO` pour les événements, jamais pour du périodique ; `WARN` demande un regard ; `ERROR` arrête. En français. **Effort** : 0,5 h. **Formation** : Recrue.

### P28. `make bag` et `procédure.md`
*Statut : Accepté.* Enregistrement daté des topics `/aeac/*` et `/mavros/*` utiles ; `procédure.md` repris de 2026 avec les noms 2027 et la ligne « `make bag` avant le décollage ». **Effort** : 1 h. **Formation** : Recrue.

---

## 10. Documentation

### P29. `ARCHITECTURE.md`, une page
*Statut : Accepté.* Tableau qui-tourne-où (1.2), schéma radio (1.3), règles (mission = workspace + YAML, langue, logs, sous-modules en trois phrases, systemd est un emballage), tableau d'adressage, section leads. **Effort** : 2 h. **Formation** : Recrue.

### P30. README : quick start en tête, puis tout ce qui aide, rien qui ment
*Statut : Accepté, précisé.* Consigne de Colin intégrée : le README peut être long. Structure : quick start (clone, `make init`, `make build C=sim`, `make sim`) en quinze lignes en tête ; puis des sections libres (dépannage Jetson, UART JetPack 5 et 6, réseau, astuces) tant qu'elles sont vraies. La seule règle : une commande citée dans le README existe dans le Makefile, et `make check` le vérifie (grep des `make <cible>` du README contre les cibles). Le guide WSL reste dans les formations.
- **Effort** : 1 h. **Formation** : Recrue.

### P33. `NOTES.md` : le journal non organisé
*Statut : Nouveau, demandé par Colin.* Un fichier à la racine où n'importe qui dépose une note en une ligne quand il n'a pas envie de la ranger : une date, un nom, le texte. Aucune structure imposée, aucune relecture exigée, jamais de ménage sans l'accord de l'auteur. C'est le successeur assumé de la section « Notes pas organisées » du README 2026, avec une différence : il est nommé pour ce qu'il est, et le README ne ment plus. Une fois par mois, un lead promeut ce qui mérite de l'être vers `ARCHITECTURE.md` ou le README, et laisse le reste.
- **Effort** : 0 h. **Formation** : Recrue (« si tu apprends quelque chose, écris-le là »).

### P31. Un README de cinq lignes par paquet
*Statut : Accepté.* Rôle, nœuds, topics (par leurs noms dans `topics.py`), paramètres. **Effort** : 1 h. **Formation** : Recrue.

---

## 11. Hors du template : ce que 2027 portera au besoin

Inchangé par rapport à la V1 : `polar_system`, `gimbal_controller`, `remote_controller_interface`, `shoot_and_capture`, contrôleurs de charge utile, serveurs web C++, `control_nav`, avec le nettoyage listé dans la revue. `TerminationSystem` n'est pas porté. `vision` est désormais un sous-module du template (P2).

---

## 12. Parallèle 2026 / 2027 pour la formation

| Sujet | aeac-2026 (branche de compétition) | aeac-2027 |
|---|---|---|
| Branche par défaut | `main` mort, code de compétition sur une branche | `main` = ce qui vole (P1) |
| Sous-modules | 8, script `--remote`, nesting à trois niveaux | 5, `make init` / `status` / `bump`, un paquet par dépôt (P2) |
| Workspaces | Un par mission, avec trois listes (symlinks git, `pkgs.txt`, bind-mounts) | Un par mission, une liste : les symlinks dans git (P11) |
| Ajouter un paquet | `pkgs.txt` + `link_ws.sh` + compose | `make link` + commit (P12) |
| Montage des conteneurs | Le workspace seul + un bind-mount par paquet | Le dépôt entier, `working_dir` sur le workspace (P6) |
| Dev, test, déploiement | Mélangés dans un Makefile de 51 cibles | Trois sections nommées ; systemd = emballage (P5, P8) |
| Dockerfiles | Trois presque identiques nommés par mission, `numpy` divergent, `pip freeze` mort | Multi-étapes ou par rôle, `requirements-*.txt` lus (P7) |
| Noms de topics | Quatre familles, quatre câblages morts | `topics.py`, préfixe unique (P15, P16) |
| Enums, PWM | Redéfinis dans trois fichiers | Constantes de `custom_interfaces` (P17) |
| Gains, coordonnées, endpoints | Copiés dans les launch et les json5 | YAML par mission, par site, json5 par drone (P19, P20, P32) |
| Tourner sans drone | Mocks éparpillés, pas de launch | `sim_mocks`, `make sim`, démo dans la formation (P24 à P26) |
| Zenoh | `router` sans scouting sur la branche, `peer` sur `main` | `router`, `ROS_LOCALHOST_ONLY=1`, `lo-multicast` (P9) |
| Doc | README 270 lignes avec « Notes pas organisées » | README vrai + `NOTES.md` journal + `ARCHITECTURE.md` (P29, P30, P33) |
| Sécurité | Readiness stubs, `TerminationSystem` mort | Vérifications réelles ou absentes, `_test` en sim seulement (P21, P22) |
| Repris tels quels | Réseau, domaines, systemd, `procédure.md`, `gcs_heartbeat`, forme d'`auto_approach` | (P8, P9, P23, P28) |

---

## 13. Récapitulatif

| # | Proposition | Effort | Formation | Statut |
|---|---|---|---|---|
| P1 | `main` = ce qui vole | 0 h | Recrue | Accepté |
| P2 | Sous-modules simplifiés, `make init/status/bump` | 4 h | Recrue / Leads | Accepté, précisé |
| P3 | `.gitignore`, `.dockerignore`, modèles hors git | 1 h | Non | Accepté |
| P4 | Métadonnées + `make check` | 2 h | Recrue | Accepté, précisé |
| P5 | Makefile en trois sections | 4 h | Recrue / Leads | Accepté, précisé |
| P6 | Compose : un montage, la commande est le launch | 2 h | Recrue | En exploration (workspaces) |
| P7 | Images et `requirements-*.txt` | 3 h | Recrue | En exploration (dockerfiles) |
| P8 | systemd : déploiement seulement | 1,5 h | Recrue / Leads | Accepté, précisé |
| P9 | Zenoh router, domaines expliqués | 1,5 h | Recrue | Accepté |
| P10 | Root dans les conteneurs | 0,5 h | Non | Accepté |
| P11 | Une mission = un workspace, symlinks git | 1 h | Recrue | En exploration (workspaces) |
| P12 | `make link` pour ajouter un paquet | 0,5 h | Recrue | En exploration (workspaces) |
| P13 | `package.xml` est le contrat | 0,5 h | Recrue | En exploration (workspaces) |
| P14 | Règle local / partagé | 0 h | Recrue / Leads | En exploration (workspaces) |
| P15 | `topics.py` | 1 h | Recrue | Accepté |
| P16 | Préfixe unique | 0,5 h | Recrue | Accepté |
| P17 | Enums dans `custom_interfaces` | 1 h | Recrue | Accepté |
| P18 | Règle de langue | 0 h | Recrue | Accepté |
| P19 | YAML par mission | 1,5 h | Recrue | Accepté |
| P20 | YAML par site | 1 h | Recrue | Accepté |
| P32 | json5 par drone | 1 h | Recrue / Leads | Accepté |
| P21 | Le code n'arme jamais, sauf `_test` en sim | 0,5 h | Recrue | Accepté, précisé |
| P22 | Pas de stub, pas de sleep | 2 h | Recrue | Accepté |
| P23 | Heartbeat défini | 1 h | Recrue | Accepté |
| P24 | `sim_mocks` | 2 h | Recrue | Accepté |
| P25 | `make sim` | 3 h | Recrue | En exploration (simulation), reformulé |
| P26 | Démo dans la formation 5 | 4 h (formation) | Recrue | En exploration (simulation), réorienté |
| P27 | Règle de logs | 0,5 h | Recrue | Accepté |
| P28 | `make bag`, `procédure.md` | 1 h | Recrue | Accepté |
| P29 | `ARCHITECTURE.md` | 2 h | Recrue / Leads | Accepté |
| P30 | README vrai, quick start en tête | 1 h | Recrue | Accepté, précisé |
| P33 | `NOTES.md` journal | 0 h | Recrue | Nouveau |
| P31 | README par paquet | 1 h | Recrue | Accepté |
| | **Total template et dépôts partagés** | **~44 h** | | |
| | **Plus la démo, côté formation** | **4 h** | | |

---

## 14. Ordre de réalisation

1. **Trancher les trois explorations** (workspaces, dockerfiles, simulation). Sans elles, l'arborescence n'est pas figée.
2. **Dépôts partagés** (P2, P4, P22) : restructurer `custom_interfaces`, `tools`, `nav_stack`, `vision` ; `topics.py`, constantes d'enum ; `make check`.
3. **Squelette** (P3, P5 sections 1 et 2, P6, P7, P9 à P14) : Makefile, compose, images, workspaces, `.gitignore`, `.dockerignore`. Jalon : `make build C=gcs` passe dans une image fraîche sous WSL.
4. **Simulation** (P19, P20, P21, P24, P25) : mocks, YAML, `make sim`. Jalon : `make sim C=<mission de test>` lance mavros, les mocks et un launch vide sans erreur.
5. **Documentation** (P27 à P31, P33, P18) : `ARCHITECTURE.md`, README, `NOTES.md`, `procédure.md`, README de paquets.
6. **Déploiement** (P5 section 3, P8, P32) : au premier passage sur une Jetson 2027.
7. **aeac-2027** : copie du template, `git init`, sous-modules, premier commit.
8. **Formation 5** : `demo_ws` (P26), rédaction sur le template, section 12 comme avant / après.

---

## 15. Commentaires de Colin sur la V1 (21 septembre 2026) et traitement

| Sujet | Commentaire | Traitement dans la V2 |
|---|---|---|
| Arborescence | Sensée. | Gardée, annotée `(?)` là où une exploration est ouverte. |
| Schémas | Pas clairs visuellement, difficiles à comprendre. | Remplacés par le tableau 1.2 et le schéma linéaire 1.3. |
| P1, P3, P9, P10, P15 à P20, P22 à P24, P27 à P29, P32 | D'accord. | Statut Accepté. |
| P2 | D'accord ; il faut des cibles Make pour simplifier le suivi des sous-modules et de l'exécution. | Tableau de cibles `init`, `status`, `bump`, `check` dans P2. |
| P4 | D'accord ; une commande pour vérifier que tout est rempli. | `make check` décrit dans P4, étendu aux liens, sous-modules, README. |
| Makefile (P5) | Sections distinctes : développement (environnements et launch de dev) et test d'un côté, déploiement sur véhicule de l'autre ; les services ne doivent pas être la seule façon de lancer ; pas obligé d'avoir tout au début. | P5 réécrit en trois sections ; règle « systemd est un emballage » dans 1.2, P5, P8 ; section 3 optionnelle au départ. |
| P6 | Pas convaincu : tout réunir et monter tout le dépôt semble plus lourd (ressources, build). À valider. | `EXPLORATION-workspaces-et-builds.md`, section 2 (ce qui coûte) ; P6 en exploration. |
| P7 | « Enlève requirements.txt » : pas sûr, comparer avec 2026, investir plus. | Malentendu levé (lu ou supprimé, pas supprimé) ; `EXPLORATION-dockerfiles-et-requirements.md` ; P7 en exploration. |
| P8 | D'accord, mais déploiement réel seulement ; dev et test différents, attention aux Jetsons. | P8 réécrit ; `make undeploy` ; règle de l'emballage. |
| P11 à P14 | À brainstormer ; préférence pour une mission = un workspace comme 2026 ; ouvert si on compare. | `EXPLORATION-workspaces-et-builds.md` (trois options, comparaison, W1 recommandée) ; P11 à P14 réécrits selon W1, en exploration. |
| P21 | D'accord ; en simulation, des nœuds de test qui arment sont corrects. | Règle des nœuds `_test` dans P21. |
| P25 | Pas sûr de comprendre. | `EXPLORATION-simulation-et-mission-demo.md`, sections 1 à 3 ; P25 reformulé avec ce que `make sim` lance ligne par ligne. |
| P26 | Pas complètement sûr ; peut-être dans la formation plutôt que dans aeac-2027. | Exploration sections 4 à 6 ; P26 réorienté : démo dans la formation 5. |
| P30 | Peut être plus long ; garder un fichier de notes non organisées, comme un journal. | P30 assoupli ; P33 `NOTES.md` créée. |
