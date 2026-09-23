# Plan d'architecture aeac-2027

*Version du 21 septembre 2026. Ce document a deux usages : c'est le plan du dépôt `aeac-2027` (et du dossier `mission-template/` dont il sera la copie), et c'est le fil de la future Formation 5, qui enseigne ce qu'un dépôt de mission doit contenir. Il part de l'architecture d'aeac-2026 et de sa revue pédagogique (`REVUE-PEDAGOGIQUE-aeac-2026.md`) ; le mécanisme de partage de code est tranché dans `BRAINSTORM-partage-de-code-2027.md`. Chaque proposition est numérotée pour être acceptée, modifiée ou refusée une par une.*

**Comment lire une proposition.** Chaque bloc `P<n>` donne : ce qu'on fait, pourquoi (avec le renvoi à la revue quand il existe), l'effort estimé, et la ligne **Formation** qui dit à qui ça s'adresse : *Recrue* (enseigné en formation 5), *Leads* (documenté dans `ARCHITECTURE.md`, section leads, jamais en formation), *Non* (fait, pas enseigné). Le tableau récapitulatif de la section 13 reprend tout.

**Décisions déjà prises** (revue section 7 et brainstorm du 21 septembre) : squelette générique seulement dans le template, code en anglais et docs/logs en français, template dans `Control-Formations/5-env_compétition/mission-template/`, sous-modules simplifiés (quatre maison plus `zed-ros2-wrapper`), dépôts partagés repris et restructurés, `vision` est un sous-module dès le départ (à rendre plus versatile), SUAS 2027 dans un dépôt séparé, `main` = ce qui vole, pas de tests, un Dockerfile par machine, root dans les conteneurs accepté à court terme.

**Source.** Le plan part de la branche `mission-2-photo-pipeline` (`71408c4`), celle qui a volé en compétition, vérifiée le 21 septembre par diff contre `main`. Trois choses y existent qui ne sont pas sur `main` et que le plan reprend : un conteneur vision séparé sur image GPU JetPack (`compose/vision.yml`, `docker/dockerfile.vision`), les missions lancées au boot par systemd (le compose exécute directement `ros2 launch`), et Zenoh en mode `router` avec `ROS_LOCALHOST_ONLY=1` et un service multicast loopback. Plus un config Zenoh sol par drone (Hexa et OS).

**Hypothèses.** Même matériel qu'en 2026 : Jetson Orin embarquée, ZED, SIYI HM30 en lien principal, LTE + Tailscale en secours, un portable GCS sous WSL, deux drones (reconnaissance et intervention). Thème 2027 inconnu jusqu'à l'automne : rien dans ce plan ne dépend des missions.

---

## 1. Vue d'ensemble

### 1.1 Arborescence cible

```
aeac-2027/
├── README.md                 quick start en 15 lignes, rien d'autre
├── ARCHITECTURE.md           une page : schéma, qui tourne où, conventions, section leads
├── procédure.md              checklist jour J, reprise de 2026
├── Makefile                  ~20 cibles, toutes documentées par ##
├── .gitignore                complet (section 2)
├── .gitmodules               custom_interfaces, tools, nav_stack, vision, zed-ros2-wrapper
├── compose/
│   ├── drone.yml             conteneur mission sur la Jetson ; sa commande est le launch de C=
│   ├── vision.yml            conteneur vision sur la Jetson (image GPU), lancé au boot
│   ├── gcs.yml               conteneur sur le portable ; sa commande est le launch GCS de C=
│   ├── sim.yml               tout sur une machine : image gcs + mavros-sim, pas de zenoh
│   ├── mavros.yml            service mavros (systemd sur la Jetson)
│   ├── zenoh-air.yml         pont Zenoh côté drone (mode router)
│   ├── zenoh-ground.yml      pont Zenoh côté GCS, config choisie par DRONE=
│   └── zed.yml               conteneur ZED (systemd sur la Jetson)
├── docker/
│   ├── dockerfile.drone      Ubuntu + ROS, en-tête : « ce qui diffère de gcs et pourquoi »
│   ├── dockerfile.vision     base l4t-jetpack (CUDA, TensorRT), en-tête idem
│   ├── dockerfile.gcs
│   └── dockerfile.mavros
├── config/
│   ├── demo.yaml             config de la mission exemple (section 6)
│   ├── sites/                cimetière.yaml, compétition.yaml : ce qui change par terrain
│   ├── drones/               hexa.json5, os.json5 : endpoints Zenoh sol vers chaque drone
│   ├── mavros.yaml
│   ├── zenoh-air.json5
│   └── zenoh-ground.json5    partie commune ; les endpoints viennent de drones/
├── packages/                 tous les paquets ROS 2, à plat
│   ├── custom_interfaces/    [sous-module] msg, srv, constantes d'enum
│   ├── tools/                [sous-module] topics.py, heartbeats, utilitaires
│   ├── nav_stack/            [sous-module] init, convert, waypoints
│   ├── vision/               [sous-module] pipeline ZED et YOLO, construit seulement si une mission en dépend
│   ├── zed-ros2-wrapper/     [sous-module tiers] hors du workspace, COLCON_IGNORE
│   ├── sim_mocks/            rc_simulator, target_mock, tout ce qui remplace le matériel
│   └── demo_bringup/         la mission exemple : launch + package.xml
├── ws/
│   ├── src -> ../packages    un seul symlink, commis
│   ├── build/<C>/            un build et un install par conteneur (ignorés)
│   └── install/<C>/
├── models/                   ignoré par git, rempli par `make models`
└── systemd/
    ├── lo-multicast.service  multicast sur loopback, requis par ROS_LOCALHOST_ONLY
    ├── mavros.service
    ├── zed.service
    ├── zenoh-air.service
    ├── vision.service
    ├── mission.service       lance compose/drone.yml avec C= lu dans /etc/aeac/mission
    └── install.md
```

Une mission réelle 2027 ajoute : `packages/<mission>_bringup/`, `packages/<mission>_*` pour ses nœuds, `config/<mission>.yaml`, et une cible `make <mission>`. Rien d'autre ne change.

### 1.2 Schéma de déploiement

```
        JETSON (drone)                        RADIO                    GCS (portable WSL)
 ┌──────────────────────────────┐    SIYI HM30 192.168.144.x    ┌──────────────────────────────┐
 │ tout démarre au boot (systemd)│    secours: LTE + Tailscale   │ make gcs C=<mission> DRONE=  │
 │   lo-multicast.service       │                               │   ┌─────────────────────┐    │
 │   mavros.service    ─┐       │                               │   │ conteneur gcs       │    │
 │   zed.service        │ DDS   │                               │   │ ROS_DOMAIN_ID=3     │    │
 │   vision.service     │ local │                               │   │ nœuds GCS, rosbag   │    │
 │   mission.service    │ dom. 2│                               │   └─────────┬───────────┘    │
 │   zenoh-air.service  │       │                               │             │ DDS local      │
 │   ┌───────────────┐  │       │                               │   zenoh-ground ◄─────────────┼── tcp/7447
 │   │conteneur drone│◄─┤       │                               │   (config/drones/<drone>)    │
 │   │ROS_DOMAIN_ID=2│  │       │                               └──────────────────────────────┘
 │   │launch mission │  │       │
 │   └───────────────┘  │       │
 │   ┌───────────────┐  │       │
 │   │conteneur vision│◄┘       │
 │   │image GPU, YOLO│          │
 │   └───────────────┘          │
 │   zenoh-air (router) ────────┼── tcp/7447 ──► seuls /aeac/external/* et /tf traversent
 │   make shell C= pour déboguer│
 └──────────────────────────────┘

 SIMULATION (une seule machine) : make sim = conteneur gcs + mavros vers SITL (tcp:5762) + sim_mocks,
 domaine 3, pas de Zenoh. La mission tourne sans drone, sans ZED, sans manette.
```

Ce schéma est la première chose que la formation 5 fait dessiner de mémoire. Il tient sur une page d'`ARCHITECTURE.md`.

---

## 2. Dépôt et Git

### P1. `main` = ce qui vole

Un seul rôle pour `main` : le code qui a volé ou qui va voler. On travaille sur une branche, on ouvre une PR, un lead fusionne. Aucune autre convention n'est enseignée (pas de format de commit, pas de nommage de branche imposé ; `prenom/sujet` suggéré dans `ARCHITECTURE.md`, sans plus).
- **Pourquoi** : en 2026, `main` est mort en avril et le code de compétition vit sur une branche (revue 1, 3.1). Enseigner un dépôt dont la branche par défaut est fausse, c'est enseigner que `main` n'a pas d'importance.
- **Effort** : 0 h dans le template ; une ligne dans `ARCHITECTURE.md` et le README.
- **Formation** : Recrue (déjà en formation 0, rappelée en 5).

### P2. Sous-modules simplifiés

Cinq sous-modules dans `packages/` : `custom_interfaces`, `tools`, `nav_stack`, `vision` (maison, un paquet ROS par dépôt, `package.xml` à la racine) et `zed-ros2-wrapper` (tiers, fork `zenith`, hors du workspace). `vision` est dans le template mais la mission `demo` n'en dépend pas : il n'est construit que quand un bringup le demande, et jamais sur la GCS. `make init` fait `git submodule update --init` et pose `submodule.recurse=true` et `push.recurseSubmodules=on-demand`. `make bump PKG=<nom>` avance un pointeur (leads). Aucun script ne fait `--remote`.
- **Pourquoi** : brainstorm section 6, options B et C comparées geste par geste. Les cinq causes de la douleur 2026 sont corrigées une par une (brainstorm 6.1).
- **Effort** : 4 h (cibles Make, restructuration des quatre dépôts partagés : `package.xml` à la racine, retrait du code mort de la revue 3.5 ; pour `vision`, correction du double `intialize_topics()` et du chargement YOLO en quatre copies, revue 3.4 et 3.5). Rendre `vision` plus versatile (capteur et modèle en paramètres) est un chantier à part, hors de ce plan.
- **Formation** : Recrue pour trois phrases (clone avec `--recurse-submodules` ; `make init` si oublié ; si `git status` parle d'un sous-module, demande à un lead). Leads pour le reste (brainstorm 6.3).

### P3. `.gitignore` complet et dépôt sans binaires

`.gitignore` du template : `build/ install/ log/ __pycache__/ *.pyc models/ *.tlog *.bin *.onnx *.pt *.engine saved_images*/ .env`. La règle `data*/` de 2026 disparaît. Les modèles de vision vont dans `models/`, ignoré, rempli par `make models` qui télécharge depuis un lien Drive écrit dans le Makefile.
- **Pourquoi** : 68 Mo de modèles dans l'historique, 42 PNG, des `.pyc`, des tlog vides (revue 0.9, 3.1). Un clone lent et sale décourage dès le premier jour.
- **Effort** : 1 h.
- **Formation** : Non (une ligne dans `ARCHITECTURE.md` : « les modèles ne vont pas dans git »).

### P4. Métadonnées de paquet remplies

Chaque `package.xml` : mainteneur réel (adresse Zenith), licence Apache 2.0 comme la racine, dépendances réelles. Fichier `LICENSE` à la racine. Les dossiers `test/` générés par `ros2 pkg create` sont supprimés à la création.
- **Pourquoi** : `maintainer=root@todo.todo`, licences `TODO`, `Liscence` (revue 3.1, 3.5) ; 13 paquets avec des tests template jamais lancés. Décision prise : pas de tests, donc pas de dossiers qui font croire qu'il y en a.
- **Effort** : 0,5 h dans le template ; la règle vaut pour chaque nouveau paquet.
- **Formation** : Recrue, sous la forme « le `package.xml` est le contrat » (section 4).

---

## 3. Infrastructure d'exécution

### P5. Makefile : vingt cibles, toutes documentées

`C=<mission>` reste le sélecteur (`dev` par défaut devient `sim`). Cibles : `help`, `print-vars`, `init`, `status`, `bump`, `models`, `build`, `up`, `down`, `shell`, `logs`, `sim`, `drone`, `gcs`, `bag`, `mavros-status|logs|restart`, `zenoh-status|logs|restart`, `zed-status|logs|restart`. Chaque cible a un `##` ; `make help` les liste toutes. `make build` fait `colcon build --packages-up-to $(C)_bringup`. Plus aucune cible ne contourne `C=` en codant son compose en dur ; les cibles par machine (`drone`, `gcs`) sont des alias qui fixent `C`.
- **Pourquoi** : 51 cibles dont 17 documentées, cibles fantômes, `payload` défini deux fois, `DOMAIN` mort (revue 3.2). Les formations 2 et 3 enseignent déjà `C=`, `help`, `print-vars` : on garde exactement ça.
- **Effort** : 3 h.
- **Formation** : Recrue (`make help`, `C=`, `build`, `shell`, `sim`, `print-vars`). Leads pour `bump`, `status`, les cibles systemd.

### P6. Compose : un mécanisme, la commande du conteneur est le launch

Tous les conteneurs montent le dépôt entier dans `/aeac` et ont `working_dir: /aeac/ws`. `drone.yml`, `vision.yml`, `gcs.yml` et `sim.yml` ne diffèrent que par l'image, `ROS_DOMAIN_ID` (2 sur le drone, 3 au sol et en sim) et les services annexes (mavros-sim dans `sim.yml`). La commande du conteneur n'est plus une boucle `sleep` : c'est `ros2 launch ${C}_bringup mission.launch.py` (ou `gcs.launch.py`, `vision.launch.py`), comme sur la branche de compétition, ce qui permet à systemd de lancer la mission au boot et de la relancer si elle tombe. `make shell C=` ouvre un second shell dans le conteneur pour déboguer. `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` et `ROS_LOCALHOST_ONLY=1` partout où Zenoh fait le pont. Plus de bind-mount paquet par paquet, plus de `pkgs.txt`, plus de `link_ws.sh`, plus de services commentés.
- **Pourquoi** : deux mécanismes de workspace en 2026, deux sources de vérité, chemins différents selon le conteneur (revue 3.2, 4.2.2). La branche `mission-2-photo-pipeline` a déjà fait passer `water.yml` et `vision.yml` au pattern « la commande est le launch » ; `main` a encore la boucle `sleep`.
- **Effort** : 2 h.
- **Formation** : Recrue (lire `sim.yml` et `drone.yml` côte à côte, voir que seule l'image change ; comprendre que sur le drone la mission tourne déjà quand on se connecte).

### P7. Un Dockerfile par rôle de conteneur

Trois images de travail : `dockerfile.drone` (Jetson, ARM, Ubuntu + ROS, sans CUDA), `dockerfile.vision` (Jetson, base `nvcr.io/nvidia/l4t-jetpack`, CUDA, TensorRT, ultralytics ; reprise de la branche de compétition), `dockerfile.gcs` (x86). Plus `dockerfile.mavros`. `drone` et `gcs` sont presque identiques et c'est assumé ; les trois premières lignes de chaque fichier disent ce qui diffère des autres et pourquoi. Même version de `numpy` partout. Le `requirements.txt` est lu par le Dockerfile ou n'existe pas. `Dockerfile.vision_test` n'est pas repris.
- **Pourquoi** : décision de la revue 4.2.1 ; la branche de compétition a isolé la vision dans son propre conteneur GPU parce que l'image ROS standard et l'image JetPack ne cohabitent pas. `numpy<2` vs `numpy<1.24` accidentel, `requirements_v1.txt` lu par personne (revue 3.2).
- **Effort** : 3 h.
- **Formation** : Recrue (formation 2 couvre déjà Docker ; ici on lit l'en-tête des trois fichiers, rien de plus). Le contenu de `dockerfile.vision` est pour le bloc B8.

### P8. systemd : tout démarre au boot, y compris la mission

Les services de la branche de compétition sont repris avec leur pattern (`ExecStartPre` qui attend le périphérique, `Restart=always`, compose en avant-plan pour `journalctl`) : `lo-multicast`, `mavros`, `zed`, `zenoh-air`, `vision`, et un seul `mission.service` à la place de `water.service` et `payload.service`, qui lit la mission active dans `/etc/aeac/mission` et lance `compose/drone.yml` avec ce `C=`. Changer de mission sur un drone = changer une ligne dans ce fichier et `make mission-restart`. Les cibles `make <service>-status|logs|restart` les pilotent. `install.md` en dix lignes.
- **Pourquoi** : c'est un des meilleurs éléments du dépôt (revue 2). Sur la branche, il y a un service par mission avec le compose codé en dur ; un service unique paramétré évite d'en créer un par mission 2027.
- **Effort** : 1 h.
- **Formation** : Recrue pour « ça démarre tout seul au boot, voilà comment on regarde si ça tourne » (les trois cibles). Leads pour l'installation.

### P9. Domaines ROS et pont Zenoh, expliqués

On garde 2 sur le drone et 3 au sol, avec le pont Zenoh entre les deux et les listes `allow` limitées à `/aeac/external.*`, `/tf`, `/tf_static`. La config reprise est celle de la branche de compétition, pas celle de `main` : Zenoh en mode `router` des deux côtés, scouting multicast et gossip désactivés, `ros_localhost_only: true`, et `ROS_LOCALHOST_ONLY=1` dans tous les conteneurs ROS, ce qui exige le service `lo-multicast` (multicast sur loopback) au boot de la Jetson. Ce choix est écrit dans `ARCHITECTURE.md` en six lignes : DDS ne sort jamais de la machine, Zenoh porte seulement ce qui est déclaré externe, deux domaines différents garantissent qu'un DDS mal configuré ne traverse jamais le lien radio par accident, et le mode router sans scouting évite que deux drones ou deux portables se découvrent par surprise sur le même réseau. Les endpoints doubles (SIYI + Tailscale) restent côté sol, par drone (P32).
- **Pourquoi** : « architecture réseau bonne mais invisible » (revue 0.7, 2, 3.2). `main` est en mode `peer` avec les topics ZED dans la liste `allow` ; la branche a corrigé les deux. Rien à changer par rapport à la branche, tout à expliquer.
- **Effort** : 1,5 h (rédaction, et test que `make sim` fonctionne avec `ROS_LOCALHOST_ONLY=1` sous WSL, sinon `sim.yml` le désactive avec un commentaire).
- **Formation** : Recrue (le nom du topic dit où il voyage ; c'est la première idée d'architecture enseignée).

### P10. Root dans les conteneurs, pour l'instant

Les conteneurs tournent en root, `UID`/`GID` disparaissent du Makefile puisqu'ils ne sont pas passés au build. Le README garde le dépannage `chown` en deux lignes. Uniformisation utilisateur `dev` reportée.
- **Pourquoi** : décision de la revue 7 (« pas très grave, uniformiser à long terme »). Mieux vaut retirer les variables mortes que laisser croire qu'elles font quelque chose.
- **Effort** : 0,5 h.
- **Formation** : Non.

---

## 4. Workspace et paquets

### P11. Un seul workspace

`ws/src` est un symlink vers `../packages`, commis dans git. Il n'y a plus de workspace par mission : la mission choisit ses paquets par les dépendances de son bringup, et `make build C=water` construit `water_bringup` et ce dont il dépend, rien d'autre. Sur la GCS, `make build C=gcs` ne touche jamais aux paquets ZED. `zed-ros2-wrapper` porte un `COLCON_IGNORE` : il se construit dans son propre conteneur. Comme plusieurs conteneurs d'images différentes partagent le même dossier sur la Jetson (drone et vision), chaque `C=` a son propre `build/<C>` et `install/<C>` (`colcon build --build-base --install-base`), et le launch source `install/<C>/setup.bash`. Un seul `src`, un build par conteneur.
- **Pourquoi** : quatre workspaces sur la branche (`vision_ws` en plus), `dev_ws` annoncé mais absent, listes de paquets divergentes (revue 1, 3.2). ROS 2 a déjà le mécanisme (`package.xml` + `--packages-up-to`), et la formation 3 l'enseigne. Les builds séparés par conteneur sont ce que les workspaces séparés faisaient pour de bon ; on garde ce bénéfice sans dupliquer les sources.
- **Effort** : 1,5 h.
- **Formation** : Recrue (jalon : `make build C=demo` puis `ros2 pkg list` montre les bons paquets).

### P12. Une mission = un paquet bringup + un YAML + une cible

`packages/<mission>_bringup/` contient le launch de la mission et un `package.xml` dont les `<exec_depend>` sont la liste des paquets de la mission. `config/<mission>.yaml` porte ce qui change (section 6). `make <mission>` = `up` + `launch`. Ajouter une mission, c'est ces trois choses ; ajouter un paquet à une mission, c'est une ligne dans `package.xml`.
- **Pourquoi** : « ajouter un paquet » demandait en 2026 d'éditer `pkgs.txt`, relancer `link_ws.sh` et éditer le compose ; la règle « partagé = sous-module, spécifique = local » était violée quatre fois (revue 1, 3.5).
- **Effort** : 1 h (le bringup de la mission `demo` sert de modèle).
- **Formation** : Recrue (jalon : ajouter un paquet à `demo` et le voir construit).

### P13. `package.xml` est le contrat

Toute dépendance Python ou ROS d'un paquet est déclarée dans son `package.xml`. Le Dockerfile installe ce que `rosdep` ne couvre pas, et le dit en commentaire. Un paquet qui ne se construit pas dans une image fraîche est un bug du paquet, pas du Dockerfile.
- **Pourquoi** : `package.xml` incomplets partout, le Dockerfile compense (revue 3.5).
- **Effort** : 0,5 h (règle écrite, appliquée aux paquets du template).
- **Formation** : Recrue (formation 3 l'enseigne ; ici on le vérifie sur un vrai paquet).

### P14. Règle « partagé ou local » en une phrase

Un paquet est local au dépôt de mission sauf si un deuxième dépôt en a besoin ou s'il est conçu pour resservir d'une année à l'autre ; à ce moment un lead en fait un sous-module. En 2027, les partagés sont `custom_interfaces`, `tools`, `nav_stack` et `vision` ; les contrôleurs de charge utile et les serveurs web sont locaux tant que rien ne le contredit.
- **Pourquoi** : la règle implicite de 2026 était saine mais jamais écrite (revue 1). `vision` est partagé parce qu'il sera rendu plus versatile pour resservir (décision du 21 septembre).
- **Effort** : 0 h.
- **Formation** : Recrue (la phrase) ; Leads (le geste).

---

## 5. Interfaces et nommage (priorité absolue)

### P15. `tools/tools/topics.py` : une table plate de noms

Un seul fichier Python de constantes, groupées par deux commentaires : externe (traverse Zenoh vers la GCS) et interne (reste sur le drone). Un nœud fait `from tools.topics import SHOOT`. Aucun nom de topic n'est écrit en littéral dans un nœud ou un launch. Les nœuds C++ éventuels lisent une copie commentée « miroir de topics.py » ou passent par un paramètre.
- **Pourquoi** : quatre liaisons mortes en compétition parce que le même topic existe sous deux à quatre noms selon le fichier (revue 3.3). Décision de la revue 4.2.3 : version minimale, pas de YAML, pas de classe.
- **Effort** : 1 h.
- **Formation** : Recrue (exercice : trouver un câblage mort avec `ros2 topic info`, puis le rendre impossible avec `topics.py`).

### P16. Préfixe unique `/aeac/internal|external/`

Toute la mission publie sous `/aeac/`. Le deuxième segment est `internal` ou `external` et décide seul de ce qui traverse la radio : la liste `allow` de Zenoh ne contient que `/aeac/external.*`, `/tf`, `/tf_static`. Le préfixe est une constante en tête de `topics.py` et dans les deux json5, et nulle part ailleurs. Les préfixes `/mission/`, `/drone/`, `/polar/` et les topics nus disparaissent.
- **Pourquoi** : quatre familles de préfixes en 2026 (revue 3.3) ; la convention interne/externe est le meilleur élément du dépôt (revue 2).
- **Effort** : 0,5 h.
- **Formation** : Recrue.

### P17. Enums et constantes dans `custom_interfaces`

Les états de machine à états, les modes (gimbal, approche) et les PWM de servos sont des constantes de message dans `custom_interfaces`, sur le modèle de `PayloadState.msg` qui existe déjà. Un enum n'est jamais redéfini dans un nœud.
- **Pourquoi** : `GimbalMode` défini trois fois, PWM d'un même servo à 1600 et 1700 selon le fichier (revue 3.3).
- **Effort** : 1 h.
- **Formation** : Recrue (lire `PayloadState.msg`, voir l'enum voyager sur le fil dans `ros2 topic echo`).

### P18. Règle de langue

Identifiants, noms de topics, commentaires de code et messages de commit en anglais. README, `ARCHITECTURE.md`, `procédure.md`, docstrings de haut niveau et messages de log en français. Écrit en une ligne dans `ARCHITECTURE.md`.
- **Pourquoi** : mélange FR/EN sans règle, `threashold`, `delais` (revue 0.12, 3.6). Décidé le 21 septembre.
- **Effort** : 0 h.
- **Formation** : Recrue (la ligne).

---

## 6. Configuration par mission et par site

### P19. `config/<mission>.yaml` porte tout ce qui change

Gains PID, canaux et PWM des servos, mapping des interrupteurs RC, coordonnées de scène, chemins de sauvegarde, seuils de détection. Les launch files n'ont plus de dicts inline : ils chargent le YAML et le passent aux nœuds. Un seul endroit change entre deux drones.
- **Pourquoi** : décision de la revue 4.2.4 ; bloc PID de 55 lignes copié trois fois et déjà divergent (revue 3.5).
- **Effort** : 1,5 h (mécanique de chargement dans le launch de `demo`, exemple commenté).
- **Formation** : Recrue (jalon : changer une valeur dans le YAML, relancer, voir l'effet sans toucher au code).

### P20. `config/sites/<site>.yaml` pour ce qui change par terrain

Un fichier par site de vol (cimetière, site de compétition) qui ne contient que les coordonnées et les altitudes. Le launch prend `site:=compétition` et fusionne ce fichier par-dessus le YAML de mission. Une latitude par défaut dans le code n'existe plus.
- **Pourquoi** : latitude par défaut `75.5` sous le commentaire « Cimetière » (revue 3.4) ; le cas d'usage réel est « on change de terrain le jour J ».
- **Effort** : 1 h.
- **Formation** : Recrue (même jalon que P19).

### P32. `config/drones/<drone>.json5` pour ce qui change par drone

Un fichier par drone (`hexa`, `os`, le nouveau drone 2027) qui ne contient que les endpoints Zenoh du drone (adresse SIYI et adresse Tailscale) et, si besoin, son port série mavros. `make gcs DRONE=hexa` choisit le fichier ; le reste de `zenoh-ground.json5` est commun. La liste des drones et de leurs adresses est le tableau « plan d'adressage » d'`ARCHITECTURE.md`.
- **Pourquoi** : sur la branche de compétition, `zenoh-ground-config.json5` et `zenoh-ground-config-os.json5` sont deux copies de 43 lignes qui diffèrent par deux adresses (`.30`/`.31` et deux IP Tailscale). La troisième copie arrive avec le drone 2027.
- **Effort** : 1 h (Zenoh ne fait pas d'include ; le Makefile assemble le fichier final dans `/tmp` à partir des deux morceaux, ou bien le compose passe les endpoints par variable d'environnement si l'image du pont le permet, à vérifier).
- **Formation** : Recrue (ligne du tableau d'adressage) ; Leads (ajouter un drone).

---

## 7. Sécurité de vol dans le code

### P21. Le code n'arme jamais et ne change jamais de mode

Règle déjà enseignée en formation 3.4, écrite dans `ARCHITECTURE.md` et respectée par la mission `demo` : le pilote arme, décolle, passe en GUIDED ; les nœuds déplacent un drone déjà en vol. Aucun service `arming` ni `set_mode` n'est appelé depuis le code de mission, sauf dans un outil de test explicitement nommé comme tel.
- **Pourquoi** : valeur non négociable de Zenith (revue 0.5). La formation 3.4 le dit déjà ; le dépôt doit le montrer.
- **Effort** : 0 h.
- **Formation** : Recrue.

### P22. Pas de vérification factice, pas de sommeil dans un callback

Deux interdits nommés : `time.sleep` dans un callback et `spin_until_future_complete` depuis un callback (deadlock). Une vérification de readiness qui retourne `True` sans vérifier n'existe pas : soit elle vérifie, soit elle n'existe pas. `nav_stack/init` est corrigé en ce sens avant d'entrer dans le template (stubs `ready = True`, `String` sur un publisher `Bool`).
- **Pourquoi** : revue 3.4 (bugs vérifiés ligne par ligne) et les deux motifs à interdire.
- **Effort** : 2 h (correction de `nav_stack/init` dans le dépôt partagé).
- **Formation** : Recrue (les deux interdits, avec le contraste QoS `init.py` vs `lap.py` comme cas d'école).

### P23. Heartbeat GCS et drone, avec un comportement défini

`tools` garde `gcs_heartbeat` (le squelette de nœud idéal de la revue) et son pendant côté drone. Le comportement en cas de perte est écrit dans `ARCHITECTURE.md` et dans le YAML (délai, action) : au minimum un log en WARN et un topic `/aeac/internal/link_ok` que la machine à états consulte. Rien de plus dans le template ; ce que fait la mission en cas de perte est une décision de mission.
- **Pourquoi** : le heartbeat existe et est bon (revue 2) ; ce qu'il déclenche n'est écrit nulle part.
- **Effort** : 1 h.
- **Formation** : Recrue (`gcs_heartbeat.py` est le premier nœud lu en formation 5).

---

## 8. La mission en simulation

### P24. `packages/sim_mocks/` regroupe tout ce qui remplace le matériel

`rc_simulator` (clavier vers `RCIn`), `target_mock` (publie une cible fixe ou mobile), et à l'avenir tout mock de capteur. Un seul paquet, un README de dix lignes qui liste chaque mock, ce qu'il remplace et le topic qu'il publie.
- **Pourquoi** : les mocks existent mais vivent dans quatre paquets, sans doc ni launch (revue 0.6, 2).
- **Effort** : 2 h (porter et nettoyer les mocks de 2026).
- **Formation** : Recrue.

### P25. `make sim` lance une mission de bout en bout sans drone

`sim.yml` + `mavros-sim` vers SITL (Mission Planner ou Gazebo, comme en formations 1 et 4) + `sim_mocks` + `<mission>_bringup` avec `sim:=true`. Les nœuds qui parlent au matériel ont un mode `sim` (paramètre) qui les branche sur les mocks. Jalon de la formation : la machine à états de `demo` passe par tous ses états, visibles dans `ros2 topic echo`.
- **Pourquoi** : « pouvoir dire à un nouveau : lance ça, et tu vois la mission tourner sans drone » (revue 0.6, précision de Colin). Les nouveaux n'auront ni Jetson ni ZED ni manette.
- **Effort** : 3 h.
- **Formation** : Recrue (c'est le cœur de la formation 5).

### P26. Une mission `demo` générique dans le template

Une machine à états de quatre états (`IDLE`, `GOTO`, `ACT`, `RETURN`) qui attend un « GO » externe, va à un waypoint du YAML, appelle un service d'action factice (un mock qui répond après deux secondes), et revient. États en constantes de `custom_interfaces`, `_transition()` unique et loggé, gardes d'état, mode `sim`, topics de `topics.py`, config du YAML. Une centaine de lignes. Elle n'a rien d'AEAC : c'est le squelette de toute mission 2027.
- **Pourquoi** : la décision « squelette + générique seulement » laisse le template sans exemple à exécuter ; la formation a besoin d'une mission qui tourne. `auto_approach.py` a la bonne forme (revue 2) ; `demo` en est la version épurée, sans le bug de garde (revue 3.4).
- **Effort** : 4 h.
- **Formation** : Recrue (lu ligne par ligne, puis modifié : ajouter un état).
- **À trancher** : c'est le seul contenu du template qui n'est pas repris de 2026. Sans lui, la formation 5 n'a rien à lancer.

---

## 9. Observabilité terrain

### P27. Logs en français, throttlés, un niveau qui veut dire quelque chose

`INFO` pour les transitions d'état et les événements, jamais pour du périodique (le périodique va en `DEBUG` ou throttlé à 0,2 Hz). `WARN` pour ce qui demande un regard, `ERROR` pour ce qui arrête la mission. Écrit en cinq lignes dans `ARCHITECTURE.md` ; `demo` le montre.
- **Pourquoi** : logs mi-FR mi-EN, `INFO` à 2 Hz (revue 0.8). Le jour J, on lit `journalctl` sous pression.
- **Effort** : 0,5 h.
- **Formation** : Recrue.

### P28. `make bag` et `procédure.md` repris

`make bag` enregistre les topics `/aeac/*` et `/mavros/*` utiles dans un dossier daté (ignoré par git). `procédure.md` est repris de 2026 (c'est le modèle de checklist jour J) avec les noms 2027 et une ligne « lancer `make bag` avant le décollage ». La section debug en escalade (topics, services systemd, réseau) reste telle quelle.
- **Pourquoi** : `procédure.md` est bon (revue 2) ; rosbags enseignés en formation 9 mais aucune cible ne les lance.
- **Effort** : 1 h.
- **Formation** : Recrue (la procédure est lue en formation 5 et suivie au premier vol).

---

## 10. Documentation

### P29. `ARCHITECTURE.md`, une page, lue en premier

Contenu dans l'ordre : le schéma de 1.2, qui tourne où (tableau machine / conteneur / service), la convention `/aeac/internal|external` et les domaines, la règle « une mission = bringup + YAML + cible », les mocks et `make sim`, les règles de langue et de log, les trois phrases sur les sous-modules. Puis une section « Pour les leads » : `make bump`, créer ou sortir un paquet partagé, tags de compétition, purge après PODR.
- **Pourquoi** : quick win 8 de la revue ; c'est le document que la formation fait lire en premier.
- **Effort** : 2 h.
- **Formation** : Recrue (tout sauf la section leads).

### P30. README de quinze lignes, rien qui ment

Quick start : clone, `make init`, `make build C=sim`, `make sim`, lien vers `ARCHITECTURE.md` et vers les formations. Le guide WSL, les notes de dépannage et les cheatsheets vivent dans Control-Formations (`DEPANNAGE.md`, formation 9), pas dans le dépôt de mission. `rosbags_cheatsheet.md` et `tuning_cheatsheet.md` ne sont pas repris.
- **Pourquoi** : README de 270 lignes dont 150 de « Notes pas organisées », cibles citées inexistantes, cheatsheet cassée (revue 3.6). Une doc qui ment coûte plus qu'aucune doc.
- **Effort** : 0,5 h.
- **Formation** : Recrue (c'est la première chose lue).

### P31. Un README de cinq lignes par paquet

Rôle, nœuds, topics consommés et publiés (par leurs noms dans `topics.py`), paramètres. Pas plus. Le template le fait pour `tools`, `nav_stack`, `sim_mocks`, `demo_bringup`.
- **Pourquoi** : aucun paquet n'a de README utile sauf `polar_system` (revue 3.6), dont la doc est désynchronisée.
- **Effort** : 1 h.
- **Formation** : Recrue (en écrire un pour son propre paquet).

---

## 11. Hors du template : ce que 2027 portera au besoin

Rien de ce qui suit n'entre dans `mission-template/` (`vision`, lui, y entre comme sous-module, voir P2). Quand le thème 2027 le demande, un lead porte le paquet dans `packages/` d'aeac-2027 après le nettoyage indiqué. Ordre de probabilité décroissante.

| Paquet 2026 | Réutilisable si | Nettoyage requis avant portage (revue) |
|---|---|---|
| `polar_system` | Approche guidée par une cible | Timer recréé à chaque goal (3.4) ; `USAGE.md` désynchronisé (3.6) ; c'est par ailleurs le paquet le mieux paramétré du dépôt (2) |
| `gimbal_controller` | Charge utile orientable | `self.target_in_aim_pub(msg)` au lieu de `.publish` ; `last_update_time` non initialisé (3.4) ; `GimbalMode` vers `custom_interfaces` (P17) |
| `remote_controller_interface` | Manette en mission | Une seule version, mapping des interrupteurs dans le YAML (P19) |
| `shoot_and_capture` / `image_transfer` | Transfert d'images vers la GCS | `shoot_controller.py` vide (3.4) ; `image_transfer.py` est le nœud le mieux écrit du dépôt, à garder comme modèle |
| Contrôleurs de charge utile (`payload`, `water_payload`, `valve`) | Largage, pompe | Une seule version ; PWM dans `custom_interfaces` (P17) ; topic `SHOOT` de `topics.py` (P15) |
| Serveurs web C++ (`payload_web_server`, `water_web_server`) | Interface GCS | Fusion des deux (500 lignes communes) ; enums en littéraux `0/1` (3.3) ; à discuter : une UI Foxglove ferait-elle le travail ? |
| `control_nav`, `mission_stats_controller` | Tour de piste, statistiques | Une seule version de `control_nav` (la version `payload`) ; `lap.py` et `state_p` sont morts |
| `TerminationSystem` | Jamais | Code mort, non porté (décision revue 7) |

---

## 12. Parallèle 2026 / 2027 pour la formation

Ce tableau est le support du « avant / après » de la formation 5. On enseigne la colonne 2027 ; la colonne 2026 sert d'illustration de pourquoi, en une phrase chacune.

| Sujet | aeac-2026 | aeac-2027 |
|---|---|---|
| Branche par défaut | `main` mort, code de compétition sur une branche | `main` = ce qui vole (P1) |
| Sous-modules | 8, script `--remote` qui déplace les pointeurs, nesting à trois niveaux | 4, `make init`, `make bump`, un paquet par dépôt (P2) |
| Workspaces | 3, listes divergentes, deux mécanismes de montage | 1, `package.xml` décide (P11, P12) |
| Ajouter un paquet à une mission | `pkgs.txt` + `link_ws.sh` + compose | Une ligne dans `package.xml` (P12) |
| Noms de topics | Quatre familles de préfixes, quatre câblages morts | `topics.py`, préfixe unique (P15, P16) |
| Enums, PWM | Redéfinis dans trois fichiers, valeurs différentes | Constantes de `custom_interfaces` (P17) |
| Gains, coordonnées | Copiés dans trois launch, latitude à 75,5 | `config/<mission>.yaml`, `config/sites/` (P19, P20) |
| Tourner sans drone | Mocks éparpillés dans quatre paquets, pas de launch | `sim_mocks`, `make sim`, mission `demo` (P24 à P26) |
| Dockerfiles | Nommés par mission, `numpy` divergent, vision isolée sur la branche seulement | Nommés par rôle (drone, vision, gcs), en-tête « ce qui diffère » (P7) |
| Démarrage de la mission | Boucle `sleep` sur `main` ; sur la branche, un service systemd par mission avec compose codé en dur | La commande du conteneur est le launch, un `mission.service` paramétré (P6, P8) |
| Zenoh | `peer` sur `main`, `router` sans scouting sur la branche ; deux configs sol copiées par drone | `router`, `ROS_LOCALHOST_ONLY=1`, `lo-multicast`, endpoints par drone dans `config/drones/` (P9, P32) |
| Builds | Un workspace par conteneur, sources dupliquées | Un `src`, un `build/<C>` par conteneur (P11) |
| Makefile | 51 cibles, 17 documentées, doublons, fantômes | 20 cibles, toutes documentées (P5) |
| Doc | README de 270 lignes, cheatsheets cassées | `ARCHITECTURE.md` une page, README quinze lignes (P29, P30) |
| Sécurité | Readiness stubs, `TerminationSystem` mort | Vérifications réelles ou absentes, deux interdits nommés (P21, P22) |
| Langue | FR/EN mélangés | Code EN, docs et logs FR (P18) |
| Ce qui n'a pas changé | Réseau Zenoh, domaines 2/3, systemd, `procédure.md`, `gcs_heartbeat`, forme de `auto_approach` | Repris tels quels (P8, P9, P23, P28) |

---

## 13. Récapitulatif des propositions

| # | Proposition | Effort | Formation | Statut |
|---|---|---|---|---|
| P1 | `main` = ce qui vole | 0 h | Recrue | Décidé (revue 7) |
| P2 | Sous-modules simplifiés (dont `vision`) | 4 h | Recrue (3 phrases) / Leads | Décidé (brainstorm 6.6, 21 sept.) |
| P3 | `.gitignore` complet, modèles hors git | 1 h | Non | À confirmer |
| P4 | Métadonnées de paquet, pas de `test/` | 0,5 h | Recrue | Décidé (revue 7) |
| P5 | Makefile vingt cibles documentées | 3 h | Recrue / Leads | À confirmer |
| P6 | Compose : un mécanisme, la commande est le launch | 2 h | Recrue | Décidé (revue 4.2.2, brainstorm) |
| P7 | Un Dockerfile par rôle (drone, vision, gcs) | 3 h | Recrue | Décidé (revue 7), vision ajouté |
| P8 | systemd : tout au boot, `mission.service` paramétré | 1 h | Recrue / Leads | À confirmer |
| P9 | Zenoh router, localhost only, expliqués | 1,5 h | Recrue | À confirmer |
| P10 | Root dans les conteneurs | 0,5 h | Non | Décidé (revue 7) |
| P11 | Un seul workspace, un build par conteneur | 1,5 h | Recrue | Décidé (brainstorm) |
| P12 | Mission = bringup + YAML + cible | 1 h | Recrue | À confirmer |
| P13 | `package.xml` est le contrat | 0,5 h | Recrue | À confirmer |
| P14 | Règle partagé / local | 0 h | Recrue / Leads | Décidé (brainstorm 6.6) |
| P15 | `topics.py` | 1 h | Recrue | Décidé (revue 7) |
| P16 | Préfixe unique `/aeac/` | 0,5 h | Recrue | À confirmer |
| P17 | Enums dans `custom_interfaces` | 1 h | Recrue | À confirmer |
| P18 | Règle de langue | 0 h | Recrue | Décidé (21 sept.) |
| P19 | YAML par mission | 1,5 h | Recrue | Décidé (revue 7) |
| P20 | YAML par site | 1 h | Recrue | À confirmer |
| P21 | Le code n'arme jamais | 0 h | Recrue | À confirmer |
| P22 | Pas de stub, pas de sleep | 2 h | Recrue | À confirmer |
| P23 | Heartbeat avec comportement défini | 1 h | Recrue | À confirmer |
| P24 | `sim_mocks` | 2 h | Recrue | À confirmer |
| P25 | `make sim` | 3 h | Recrue | À confirmer |
| P26 | Mission `demo` | 4 h | Recrue | **À trancher** |
| P27 | Règle de logs | 0,5 h | Recrue | À confirmer |
| P28 | `make bag`, `procédure.md` | 1 h | Recrue | À confirmer |
| P29 | `ARCHITECTURE.md` | 2 h | Recrue / Leads | Décidé (revue 4.1.8) |
| P30 | README quinze lignes | 0,5 h | Recrue | À confirmer |
| P31 | README par paquet | 1 h | Recrue | À confirmer |
| P32 | Config par drone (endpoints Zenoh) | 1 h | Recrue / Leads | À confirmer |
| | **Total** | **~43 h** | | |

Répartition : template (P3, P5 à P13, P15 à P32) environ 37 h ; restructuration des quatre dépôts partagés (P2, P22) environ 6 h. Le portage de paquets 2026 (section 11) n'est pas compté : il dépend du thème.

---

## 14. Ordre de réalisation

1. **Dépôts partagés** (P2, P4, P22) : restructurer `custom_interfaces`, `tools`, `nav_stack`, `vision` sur `main` (un paquet à la racine, code mort retiré, `init` corrigé), y ajouter `topics.py` et les constantes d'enum. Prérequis de tout le reste.
2. **Squelette du template** (P3, P5 à P11, P13) : Makefile, compose, Dockerfiles, `ws/src`, `.gitignore`, systemd. Jalon : `make build C=sim` passe dans une image fraîche.
3. **Mission `demo` et simulation** (P12, P19, P20, P24 à P26) : mocks, YAML, bringup, `make sim`. Jalon : la machine à états passe par ses quatre états sans drone.
4. **Documentation** (P29 à P31, P18, P27, P28) : `ARCHITECTURE.md`, README, procédure, README de paquets. Jalon : une recrue qui n'a jamais vu le dépôt fait `make sim` en suivant seulement le README.
5. **aeac-2027** : copie du dossier `mission-template/`, `git init`, `git submodule add` des cinq sous-modules, premier commit. Le dépôt existant (README seul) est écrasé.
6. **Formation 5** : rédigée sur le template, en suivant le fil de la revue section 6 (sept jalons), avec la section 12 comme « avant / après ».

---

## 15. Questions ouvertes

- **P26** : la mission `demo` est-elle acceptée comme seul contenu neuf du template ?
- **Serveurs web C++** : maintenus en 2027, ou remplacés par Foxglove côté GCS ? Ça décide si du C++ entre dans les formations (question 5 de l'audit B1-B3).
- **Modèles de vision** (P3) : lien Drive dans le Makefile, ou GitHub Release ?
- **Nom des missions 2027** dans le Makefile : `recon` et `intervention` par défaut, à renommer quand le thème est connu ?
- **Purge après PODR** : qui la fait, et le tag `aeac-2027` est-il posé le jour du départ ou après la compétition ?
