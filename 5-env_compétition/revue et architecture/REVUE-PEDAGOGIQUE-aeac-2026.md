# Revue pédagogique du dépôt aeac-2026

*Objectif : décider ce qu'on enseigne, ce qu'on corrige avant d'enseigner, et ce qu'on présente comme « à ne pas faire » dans la future Formation 5 (architecture d'un dépôt de mission). Revue faite le 18 septembre 2026 sur `main` (`051e061`) et sur la branche `mission-2-photo-pipeline` (`6037652`), sous-modules inclus. Révisée le même jour après les commentaires de Colin (section 7).*

Les chemins sont relatifs à la racine du dépôt. Les numéros de ligne renvoient à la branche `mission-2-photo-pipeline` pour le code des `workspaces/` et des `packages/`, et à `main` pour le Makefile, les compose et la doc, sauf mention contraire.

---

## 0. Angles morts : critères à ajouter à la revue

Dimensions qui n'étaient pas dans la demande initiale et qui pèsent sur ce que les nouveaux vont reproduire en 2027.

| # | Critère | Pourquoi ça compte pour la formation | Constat en une ligne |
|---|---|---|---|
| 1 | **Git minimal** (`main`, branche, PR, sous-modules) | C'est la première chose qu'un nouveau copie. On reste au strict nécessaire. | `main` ne contient pas le code qui a volé en compétition. |
| 2 | **Contrat d'interfaces** (noms de topics, enums, messages) | Cause racine de la majorité des bugs trouvés. | Le même topic existe sous 2 à 4 noms selon le fichier. |
| 3 | **Configuration vs code** (IP, PWM, gains, chemins, coordonnées) | Distinguer « ce qui change par mission » de « ce qui est du code ». | PWM des servos dans 3 fichiers, gains PID copiés 3 fois. |
| 4 | **Reproductibilité** (package.xml, sous-modules, images) | Un dépôt qu'on ne peut pas rebâtir en 2027 n'enseigne rien. | package.xml incomplets partout, `ensure_submodules.sh` déplace les pointeurs. |
| 5 | **Sécurité de vol dans le code** | Valeur non négociable de Zenith, et les formations le répètent. | Readiness stubs (`ready = True`) dans `init` ; `TerminationSystem` jamais utilisé en vol et non fonctionnel. |
| 6 | **Mission en simulation** (SITL + mocks ROS) | Les nouveaux n'auront ni Jetson ni ZED ni manette. | SITL couvre l'autopilote ; les mocks ROS (RC, cible, détection) existent mais sont éparpillés et sans launch `sim`. |
| 7 | **Schéma de déploiement** (quoi tourne où : Jetson, GCS, domaines, Zenoh) | L'architecture réseau est bonne mais invisible. | Aucun schéma ; domaine 3 vs 2 non expliqué. |
| 8 | **Observabilité terrain** (logs, rosbags, journalctl, procédure) | Ce qu'on regarde quand ça casse le jour J. | `procédure.md` est bon ; logs mi-FR mi-EN, INFO à 2 Hz. |
| 9 | **Hygiène du dépôt** (binaires, artefacts, .gitignore) | Un clone lent et sale décourage dès le premier jour. | 68 Mo de modèles dans l'historique, 42 PNG, des `.pyc`. |
| 10 | **Documentation vivante** (README, cheatsheets, doc de package) | Une doc qui ment coûte plus qu'aucune doc. | Cibles Make citées mais inexistantes ; `USAGE.md` de polar désynchronisé. |
| 11 | **Générique vs spécifique** (ce qui survit à 2027) | Le but de la formation est l'architecture, pas AEAC 2026. | Aucune frontière explicite ; nom du dépôt = année. |
| 12 | **Langue et conventions** (FR/EN, nommage) | Sans règle, chaque nouveau invente la sienne. | Code EN, logs FR/EN, `threashold`, `delais`. |

**Précision sur le critère 6.** SITL (via Mission Planner ou Gazebo) simule l'autopilote, et ça marche déjà. Ce qu'il ne simule pas : les détections de la ZED, les interrupteurs de la manette, la cible. Le dépôt a des mocks ROS pour ça (`rc_simulator`, `fake_polar_target`, `target_detection_mock`, mode `sim` de `auto_approach`), mais ils vivent dans quatre paquets différents, aucune doc ne les liste, et aucun launch n'assemble « la mission en sim ». Le critère, c'est ça : pouvoir dire à un nouveau « lance ça, et tu vois la mission 2 tourner sans drone ».

---

## 1. Ce que le dépôt est vraiment (état des lieux)

**Deux copies locales, deux branches.** `~/formations/aeac-2026` est sur `main` (sous-modules non initialisés). `~/aeac-2026` est sur `mission-2-photo-pipeline`. Si la formation est bâtie sur `main`, elle enseigne du code d'avant la compétition.

**`main` est mort depuis avril.** Chiffres tirés de `git log` :

| Mesure | Valeur |
|---|---|
| Commits totaux | 288 |
| Commits sur `mission-2-photo-pipeline` absents de `main` | 91 (dernier : 2026-05-22) |
| Commits sur `left-right-payload` absents de `main` | 70 |
| Branches distantes | 23, dont 14 déjà fusionnées et jamais supprimées |
| Tags | 0 |
| Auteurs | 2 personnes font 281 commits sur 288 |

Le code de compétition vit sur une branche de fonctionnalité. Décision : fusionner `mission-2-photo-pipeline` dans `main` ; `main` = ce qui vole.

**Pointeurs de sous-modules qui dérivent.** `.gitmodules` dit `polar_system` sur `main` et `zed-ros2-wrapper` sur `zenith`. Le checkout local est sur `add-completion-topic-param` et `master`. La cause est `scripts/ensure_submodules.sh:18`, qui fait `git submodule update --remote --merge` : l'étape 3 écrase le pointeur figé du superprojet par la tête de branche.

**Layout réel des workspaces.** Trois workspaces (`payload_ws`, `water_ws`, `ground_station_ws`), pas de `dev_ws` malgré `C ?= dev`. Les paquets partagés sont des sous-modules dans `packages/`, liés par `pkgs.txt` + `scripts/link_ws.sh` (symlinks relatifs). Les paquets spécifiques à une mission vivent directement dans `workspaces/*/src`. La règle implicite « partagé = sous-module, spécifique = local » est saine mais violée quatre fois (section 3.5).

**Où est la machine à états.** Pas dans `packages/` malgré le README (« `state*` »). Mission 1 : `workspaces/payload_ws/src/mission_stats_controller`. Mission 2 : `workspaces/water_ws/src/state_w/state_w/auto_approach.py`. `state_p` est un paquet vide depuis novembre 2025.

---

## 2. Ce qui est bien fait (à enseigner tel quel)

**Architecture réseau et convention de nommage.** C'est le meilleur élément du dépôt et il n'est documenté nulle part.
- `config/zenoh-air-config.json5:6-18` et `zenoh-ground-config.json5` : listes `allow` limitées à `/aeac/external.*`, `/tf`, `/tf_static`. Seul ce qui est explicitement « externe » traverse le lien radio.
- `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` dans les compose + `ros_localhost_only: true` côté Zenoh : DDS reste local, Zenoh fait le pont. Cohérent avec le contexte Zenith (Cyclone local, Zenoh inter-machines).
- Convention `/aeac/internal/...` (bord) vs `/aeac/external/...` (traverse vers la GCS). Idée d'architecture à enseigner en premier : le nom du topic dit où il voyage.
- Endpoints doubles (SIYI + Tailscale) dans `zenoh-ground-config.json5:34-37` : le lien de secours est dans la config, pas dans la tête de quelqu'un.

**Infra d'exécution.**
- `systemd/*.service` : attente du périphérique (`ExecStartPre` jusqu'à `/dev/ttyTHS1` ou `lsusb`), `Restart=always`, compose en avant-plan pour que `journalctl` voie les logs. Cibles `make mavros-status|logs|restart`. Le pattern à montrer pour « ça démarre tout seul au boot ».
- `procédure.md` : court, ordonné, avec une section debug en escalade. Le modèle de la « checklist jour J ».
- `scripts/link_ws.sh:22-28` : symlinks relatifs qui marchent sur l'hôte et dans le conteneur.
- Makefile : `C=<mission>` pour choisir le compose, `help` auto-généré depuis les `##`, `print-vars` pour déboguer. Les Formations 2 et 3 s'appuient déjà dessus.
- MAVROS dans son propre service (`compose/mavros.yml`) plutôt que dans le conteneur de travail : c'est ce que la Formation 2 enseigne.
- Un Dockerfile par machine (drone, GCS), presque identiques : accepté et assumé. Le seul point à surveiller est que les différences soient voulues (voir 3.2).

**Code ROS 2 (exemples à pointer dans la formation).**
- `packages/tools/tools/tools/gcs_heartbeat.py` (75 lignes) : le squelette de nœud idéal. Params, timer, log throttlé, `main` propre.
- `packages/nav_stack/nav_stack/nav_stack/convert.py` : un service, une responsabilité, nom de service relatif, garde `home_set`.
- `packages/polar_system/.../position_system.py:400-452` : tous les topics en paramètres, déclaration générique des 10 PID en boucle, QoS BEST_EFFORT explicite pour MAVROS, timers créés quand les entrées sont prêtes, `publish_zero` à l'arrêt. Et `docs/USAGE.md`, la seule vraie doc de paquet.
- `packages/bringup/.../vision_mission1_pipeline.launch.py` : `DeclareLaunchArgument` avec descriptions, `TimerAction` pour échelonner, `LogInfo`. Le seul launch idiomatique du dépôt.
- `workspaces/water_ws/src/state_w/state_w/auto_approach.py:20-83` : états en constantes, `_transition()` unique et loggé, gardes `_assert_state()`, mode `sim`. Bonne forme de machine à états, une fois le bug de la garde corrigé.
- `workspaces/payload_ws/src/payload/payload/PayloadController.py:23-86` : service async qui `await` un client MAVROS, `ReentrantCallbackGroup` + `MultiThreadedExecutor`. Le bon patron rclpy pour « appeler un service depuis un service ».
- `custom_interfaces/msg/PayloadState.msg` : l'enum d'états voyage sur le fil. `SceneFrame.msg` : champs commentés.
- `workspaces/water_ws/src/shoot_and_capture/.../image_transfer.py` : docstring, dataclass, params, watchdog, ACK/retry, verrous. Le nœud le mieux écrit du dépôt.
- `control_nav.py:88-89,142-158` : données de mission (JSON de waypoints) dans `share/config` via `data_files`, chargées par `get_package_share_directory`.
- Contraste QoS `init.py:128` (BEST_EFFORT, reçoit) vs `lap.py:88` (RELIABLE, ne recevra jamais rien de MAVROS) : cas d'école prêt à l'emploi.

**Mocks pour tourner sans drone**, à regrouper mais déjà là : `rc_simulator.py` (clavier vers RCIn), `fake_polar_target`, `target_detection_mock`, mode `sim` de `auto_approach`, `mavros-sim` / `mavros-gazebo`.

---

## 3. Mauvaises pratiques : à corriger avant de montrer, ou à montrer comme contre-exemple

### 3.1 Dépôt (le strict nécessaire pour les nouveaux)

Ce qu'on enseigne se limite à trois règles : `main` = ce qui vole, on travaille sur une branche et on ouvre une PR (déjà en Formation 0), et le piège des sous-modules. Le reste ci-dessous est pour les leads.

- **Le code de compétition n'est pas sur `main`** (section 1). Enseigner un dépôt dont la branche par défaut est fausse, c'est enseigner que `main` n'a pas d'importance.
- **Artefacts suivis par git** : `models/*.onnx` (68 Mo dans l'historique sur trois fichiers), `workspaces/payload_ws/saved_images/` et `saved_images copy/` (2 × 21 PNG identiques), `__pycache__/*.pyc` (dont le bytecode d'un launch dont la source n'existe plus), `mav.tlog` vides, `lap_waypoints_colin.json`. `.gitignore` n'a ni `__pycache__/` ni `*.pyc`, et sa règle `data*/` ignore silencieusement tout dossier `data/` d'un paquet.
- **`ensure_submodules.sh` avec `--remote --merge`** : voir section 1. Le README dit « update submodules so everything is up to date » sans dire que ça sort du commit figé.
- **Nesting des sous-modules** : `packages/nav_stack/nav_stack/nav_stack/init.py`. Le dépôt contient un dossier de paquet qui contient un module. Trois niveaux du même nom, déroutant pour un nouveau qui cherche « le fichier ».
- **Fichier `Liscence`** (faute), licences `TODO` dans tous les `package.xml`, `maintainer=root@todo.todo`.
- Pour les leads seulement, pas pour la formation : 14 branches fusionnées jamais supprimées, aucun tag de compétition, messages de commit sans forme (« fixed », « yes »).

### 3.2 Makefile, compose, Docker

- **Makefile sur `main` définit `payload` deux fois** (lignes 115 et 242) ; `make` avertit à chaque appel. Corrigé sur la branche.
- **Cibles fantômes** : `relay` et `relay-down` sont dans `.PHONY` et dans le README mais n'existent pas. `makefile_cheatsheet.md` cite `water-stack`, `water-stack-build`, `payload-mission-sim` : inexistants. `make vision` lance `vision_mission.launch.py`, qui n'existe pas.
- **Variables mortes** : `DOMAIN ?= 2` n'est utilisé nulle part (les compose codent 3 ou 2 en dur). `UID`/`GID` sont exportés mais jamais passés en `build args` ; l'utilisateur `dev` créé dans l'image n'est pas utilisé et tout tourne en root, d'où le dépannage `chown` du README. Pas grave à court terme ; à uniformiser à long terme.
- **`C=` contourné** : `payload`, `water`, `gcs-*`, `mavros-jetson`, `zed-*` codent leur compose en dur. Sur 51 cibles, 17 ont un `##` et apparaissent dans `make help`. Le reste est invisible.
- **Deux mécanismes de workspace** : `dev.yml` monte tout le dépôt dans `/aeac` et compte sur les symlinks de `link_ws.sh` ; `payload.yml` et `water.yml` montent le workspace puis chaque paquet un par un (`compose/payload.yml:10-17`). `pkgs.txt` et les volumes compose sont deux sources de vérité. `payload_ws/pkgs.txt` liste `polar_system`, mais le symlink n'existe pas. Détail en 4.2.2.
- **Dockerfiles** : `dockerfile.dev`, `.payload`, `.water` sont volontairement presque identiques (accepté). Deux choses à régler quand même : ils sont nommés par mission alors qu'ils correspondent à des machines (drone, GCS), et la différence `numpy<2` vs `numpy<1.24` a l'air accidentelle. `requirements_v1.txt` est un `pip freeze` de Jetson qu'aucun Dockerfile ne lit. `Dockerfile.vision_test` se termine par une commande `docker run` collée dans le fichier.
- **60 lignes de services commentés** (zed, zenoh) dans `payload.yml` et `water.yml`, remplacées par systemd sans que le fichier le dise.
- **Domaines ROS** : 3 pour dev/ground, 2 pour air. C'est volontaire (le pont Zenoh relie deux domaines) mais aucune ligne ne l'explique.
- **`relay.yml`** : `context: .` avec `dockerfile: ../docker/...`, seul compose à faire ça ; le README avoue « quite buggy ».

### 3.3 Interfaces et nommage (la source des bugs, priorité absolue)

Quatre familles de préfixes coexistent : `/aeac/internal|external/`, `/mission/`, `/drone/`, `/polar/`, plus des topics nus (`/shoot_topic`, `/valve_state`). Résultat, des liaisons mortes en compétition :

| Émetteur | Récepteur | Effet |
|---|---|---|
| `remote_controller_interface.py:36-37` publie `/mission/control_nav/lap/finish` | `control_nav.py:57` écoute `/aeac/external/mission/control_nav/lap/finish` | L'interrupteur « finir le tour » ne fait rien. |
| `auto_approach.py:179` publie `/aeac/internal/shoot` | `valve.py` écoute `/shoot_topic` | La valve ne tire jamais par la machine à états. |
| `polar.launch.py:16-17` configure `polar` sur `/goal_pose_polar` | `controller_interface.py:65` publie `/polar/goal_pose` | La RC ne parle jamais au contrôleur polaire. |
| Centre estimé | 4 noms différents selon le fichier | Dépend du launch utilisé. |

Même chose pour les enums : `GimbalMode` défini dans `gimbal_mavros.py:42-45`, redéfini dans `auto_approach.py:15-18`, et en littéraux `0/1` dans `water_web_server_node.cpp`. Les PWM de servos vivent dans `rci.py`, `valve.py` et `script.js` avec des valeurs différentes (1600 vs 1700 pour le même servo).

Leçon : un paquet d'interfaces existe déjà (`custom_interfaces`, bonne idée). Il manque le même traitement pour les **noms** de topics et les **constantes**. Solution simple en 4.2.3.

### 3.4 Bugs vérifiés ligne par ligne

À corriger avant de faire lire le code. Les lignes `TerminationSystem` sont listées pour mémoire : le nœud n'a jamais été utilisé en vol, c'est du code mort à retirer ou à finir, pas un système de sécurité défaillant.

| Fichier | Ligne | Bug |
|---|---|---|
| `nav_stack/.../init.py` | 313 | Publie un `String` sur un publisher `Bool` (ligne 122) : l'abort global plante le nœud. |
| `nav_stack/.../init.py` | 211, 235-236 | `internal_ok/ready/external_ok = True` : les vérifications avant « GO » sont des stubs. |
| `vision/.../rgb_yolo.py` | 52 et 57 | `intialize_topics()` appelé deux fois : double inférence, double publication. |
| `gimbal_controller/.../gimbal_mavros.py` | 282, 285 | `self.target_in_aim_pub(msg)` au lieu de `.publish(msg)` : TypeError en AUTO_AIM. `last_update_time` jamais initialisé (268). |
| `control_nav/.../control_nav.py` | 104 | Latitude par défaut `75.505881` sous le commentaire « Cimetière ». Montréal est à 45.5. |
| `state_w/.../auto_approach.py` | 66-67 | `_assert_state` retourne `None` quand `ignore_state_check=True` : tous les callbacks gardés sortent. Le paramètre fait l'inverse de son intention. |
| `water_payload/setup.py` vs `water_mission.launch.py` | 28 vs 124 | Exécutable `valve_controller` déclaré, `valve` lancé. |
| `shoot_and_capture/.../shoot_controller.py` | fichier de 0 octet | Entry point déclaré vers un fichier vide. |
| `polar_system/.../position_system.py` | 1006 | Nouveau timer à chaque goal sans détruire l'ancien. |
| `TerminationSystem` (jamais utilisé) | `setup.py`, `termination.py:93`, `fence.py:35-70` | Aucun entry point ; f-string invalide ; méthodes définies deux fois. |

Deux motifs à nommer comme interdits dans la formation : `time.sleep` dans un callback (`target_detection_mock.py:45`, `gimbal_test_node.py:71`), et `spin_until_future_complete` depuis un callback (`termination.py:150,176`, deadlock).

### 3.5 Duplication et code mort

- `control_nav` en deux versions (payload à jour, water = fork périmé et non lancé). `remote_controller_interface` en deux versions (seul le dict de mapping diffère). `PayloadController.py` identique dans `payload/` et `water_payload/`. Deux serveurs web C++ à ~500 lignes communes (le include guard de `payload_web_server_node.hpp:1` est `WATER_...`).
- Bloc de gains PID de 55 lignes copié dans trois launch files, déjà divergent (`pid_yaw`).
- `setup_message_intervals` en 4 copies ; chargement du modèle YOLO en 4 copies.
- Morts : `state_p` (vide), `lap.py` (copie obsolète de `init`), `vision_node.py`, `rgb_subscriber.py`, `mission.launch.py` et `polar.launch.py` (lancent des paquets `UI` et `mission` inexistants), `nav2.launch.py` (chemin placeholder), `upload_controller` (importe un message qui n'existe pas), entry points `extract_relative_pose` et `detect_circle` vers des modules absents, `TerminationSystem`.
- 13 paquets ont les mêmes `test_copyright.py`, `test_flake8.py`, `test_pep257.py` (md5 identiques, templates de `ros2 pkg create`). Décision : pas de tests, donc les supprimer pour ne pas laisser croire qu'il y en a.
- `package.xml` incomplets dans tous les paquets. C'est le Dockerfile qui compense. Leçon : le `package.xml` est le contrat, pas le Dockerfile.

### 3.6 Documentation

- README : « Essentials » pendant 120 lignes puis « Notes pas organisées » pendant 150 lignes, avec des commandes contradictoires (`mavlink-routerd` en trois variantes), un guide WSL complet qui appartient aux formations. Cite `C=recon`, `zenoh/config.json5`, `packages/state*` : inexistants.
- `rosbags_cheatsheet.md` : contenu dupliqué et cassé après la ligne 104. `tuning_cheatsheet.md` : trois `sysctl` sans une ligne d'explication.
- `polar_system/docs/USAGE.md` : cite un launch, un exécutable et un dossier `config/` qui n'existent pas.
- Aucun paquet n'a de README utile sauf `polar_system` et `vision` (dont le README est des notes ZED).
- Mélange FR/EN dans les logs, les commentaires et les commits, sans règle.

---

## 4. Optimisations proposées (proche de l'existant, pas de refonte)

### 4.1 Quick wins (une soirée, avant la première cohorte)

1. **Fusionner `mission-2-photo-pipeline` dans `main`** (décidé). Décider du sort de `left-right-payload` (70 commits, base commune du 16 mai).
2. **Purger le dépôt** : PNG, `.pyc`, tlog, JSON perso ; ajouter `__pycache__/`, `*.pyc`, `saved_images*/` au `.gitignore`, retirer `data*/`. Sortir les `.onnx`/`.pt` de l'historique n'est pas obligatoire ; au minimum, ne plus en ajouter.
3. **Makefile** : supprimer le doublon `payload`, retirer `relay*` et `DOMAIN`, corriger `vision`, mettre un `##` sur les 34 cibles muettes. **README** : retirer `recon`, `zenoh/`, `state*`, déplacer le bloc WSL vers `Formations-Controle/DEPANNAGE.md` (déjà couvert), supprimer la section « Notes pas organisées » après avoir sauvé les 4 lignes utiles (UART JetPack 5/6). Corriger les cheatsheets.
4. **Corriger les bugs de la table 3.4** et les 3 câblages de la table 3.3. Un après-midi.
5. **Supprimer le code mort** listé en 3.5, les entry points fantômes et les dossiers `test/` template.
6. **Remplir `package.xml`** et `setup.py` (maintainer, licence Apache 2.0 comme la racine, deps réelles).
7. **Retirer l'étape 3 de `ensure_submodules.sh`** (ou la mettre derrière un flag `--latest`). Remettre les sous-modules sur les branches de `.gitmodules`.
8. **Écrire `ARCHITECTURE.md`** d'une page : schéma Jetson/GCS, quel conteneur tourne où, domaines 2 et 3, pont Zenoh, convention `/aeac/internal|external`, liste des mocks. C'est le document que la formation fera lire en premier.

### 4.2 Structurel (dépôt 2027, ou à enseigner comme « ce qu'on change »)

**1. Dockerfiles : un par machine.** Décision : un Dockerfile par drone et un pour la GCS, presque identiques, et c'est assumé. Ce qui change par rapport à aujourd'hui : les nommer par machine (`dockerfile.drone`, `dockerfile.gcs`) plutôt que par mission, et mettre en tête de chaque fichier un commentaire de trois lignes « ce qui diffère de l'autre et pourquoi ». La divergence `numpy` se règle au passage.

**2. Un seul mécanisme de workspace.** Aujourd'hui il y en a deux :

- *Mécanisme A* (`dev.yml`) : tout le dépôt est monté dans `/aeac`. Le `src/` de chaque workspace contient des symlinks relatifs vers `../../../packages/<pkg>`, créés par `link_ws.sh` à partir de `pkgs.txt`. Les mêmes chemins existent sur l'hôte et dans le conteneur ; `git` marche dans le conteneur ; ajouter un paquet = une ligne dans `pkgs.txt` + `make link`.
- *Mécanisme B* (`payload.yml`, `water.yml`) : seul le workspace est monté (`/payload_ws`), puis chaque paquet de `packages/` est bind-mounté un par un dans `/payload_ws/src/<pkg>`. `pkgs.txt` est ignoré ; ajouter un paquet = éditer le compose. Les symlinks du mécanisme A pointent vers `../../../packages`, qui n'existe pas dans ce conteneur : ils sont pendants, et le bind-mount les recouvre. Ça marche par accident.

Conséquences concrètes : deux listes de paquets à tenir à jour (le `polar_system` manquant dans `payload_ws/src` en est le symptôme), des chemins différents selon le conteneur (`/aeac/workspaces/water_ws` vs `/water_ws`), donc les chemins codés en dur dans les nœuds (`/water_ws/snapshots`, `/water_ws/Pictures`) cassent dès qu'on change de conteneur, et une explication deux fois plus longue pour un nouveau.

Recommandation : garder A partout. Chaque compose de mission devient cinq lignes identiques (monter le dépôt dans `/aeac`, `working_dir: /aeac/workspaces/<mission>_ws`), seule l'image change. `pkgs.txt` devient l'unique endroit qui dit « quels paquets partagés cette mission utilise », et c'est ce qu'on enseigne. Si on préfère B, il faut alors supprimer `pkgs.txt` et `link_ws.sh` pour qu'il n'y ait qu'une source de vérité, et accepter que le build sur l'hôte ne marche plus.

**3. Une table unique des noms, version minimale.** Pas de YAML, pas de remapping, pas de classe. Un seul fichier Python `tools/tools/topics.py` avec des constantes plates, groupées par deux commentaires (`# externe : traverse Zenoh vers la GCS` / `# interne : reste sur le drone`) :

```python
# externe : traverse Zenoh vers la GCS
MISSION_GO        = "/aeac/external/mission/go"
LAP_FINISH        = "/aeac/external/mission/control_nav/lap/finish"
UI_DISPLAY        = "/aeac/external/UI/display"
# interne : reste sur le drone
SHOOT             = "/aeac/internal/shoot"
TARGET_ERROR      = "/aeac/internal/gimbal/target_error"
```

Et dans un nœud : `from tools.topics import SHOOT`. Un nouveau comprend ça en trente secondes, `grep` retrouve tous les usages, et les quatre câblages morts de la table 3.3 deviennent impossibles. Les enums (`GimbalMode`, `ApproachState`) vont dans `custom_interfaces` comme constantes de message, sur le modèle de `PayloadState.msg` qui existe déjà. Les deux serveurs C++ lisent la même table via `custom_interfaces` ou une copie commentée « miroir de topics.py ».

**4. Config YAML par mission** (décidé). Un `bringup/config/<mission>.yaml` par mission qui porte tout ce qui change entre deux sites de vol ou deux drones : gains PID, PWM et canaux des servos, coordonnées de scène, mapping des interrupteurs RC, chemins de sauvegarde. Les launch files ne contiennent plus de dicts inline. Un seul endroit change entre le cimetière et le site de compétition.

**5. Dédupliquer, sans `mission_common`.** L'objectif est acquis (une seule version de `control_nav`, de `remote_controller_interface`, du contrôleur de servos, du serveur web). Sur l'emplacement, deux options plus proches de l'existant qu'un nouveau paquet fourre-tout :
- *Option a* : chaque paquet dédupliqué devient un sous-module dans `packages/`, comme les autres paquets partagés. C'est la règle actuelle appliquée jusqu'au bout ; le mapping par mission vient du YAML du point 4.
- *Option b* : les petits (`rc_interface`, `servo_controller`) rejoignent `tools`, qui contient déjà les heartbeats ; seul le serveur web reste un paquet à part.
Option a garde la règle simple à expliquer (« partagé = `packages/` »). À trancher avec le point 9.

**6. Dev et utilisateur non-root** : à uniformiser à long terme, pas prioritaire.

**7. `main` = ce qui vole.** Après la fusion, c'est la seule règle git qu'on enseigne en plus de « branche + PR ».

**8. Template de dépôt pour 2027** (décidé, à brainstormer). Pistes de départ :
- Contenu minimal : Makefile, `compose/`, `docker/` (drone + gcs), `packages/custom_interfaces` et `packages/tools` (avec `topics.py`), `bringup` avec un launch et un YAML vides, `systemd/`, `ARCHITECTURE.md`, `procédure.md`, `.gitignore` complet.
- Question ouverte : dépôt GitHub « template » (bouton *Use this template*, historique vierge) ou branche `template` dans le dépôt de l'année ?
- Question ouverte : ce qui est spécifique à AEAC (missions, ZED, gimbal) reste-t-il dans le template comme exemple commenté, ou hors du template ?
- Question ouverte : combien de sous-modules ? Le nesting à trois niveaux et la dérive des pointeurs plaident pour peu (interfaces, tools, bringup), pas pour un par paquet.

---

## 5. Cohérence avec les Formations-Controle

Corrigé le 18 septembre 2026 dans les fichiers de formation :

| Formation | Avant | Après |
|---|---|---|
| `3.1:510` | « Tout aeac-2026 est écrit en Python » | Presque tout ; les serveurs web de la station sol sont en C++. |
| `3.3:58` | Workspaces « empilés » comme dans aeac-2026 | aeac-2026 a un workspace par mission, côte à côte, un seul sourcé par conteneur. |
| `DEPANNAGE.md:34` | `ROS_DOMAIN_ID` « 2 partout » | Les compose des formations mettent 2 ; dans aeac-2026, 2 côté drone et 3 côté sol, par design. |
| `2:636` | `make mavros-sim` « est notre `listen-status` », `make help` « liste tout » | Même rôle mais mavros lancé dans le conteneur de travail ; `help` liste les cibles documentées. |
| `3.4:216` | « la structure des nodes d'aeac-2026 » | « des nodes les plus récents d'aeac-2026 (`auto_approach`, `valve`) ». |

Non modifié : `3.4:49` (« `nav_stack/init`, qu'on lit dans la formation 5 ») reste vrai une fois le bug de la ligne 313 corrigé. La table de `3.3:89-103` pointe vers des fichiers qui existent ; les deux entrées vers `gimbal_test_node` désignent un outil de test, à requalifier quand la Formation 5 sera écrite.

Note : aucune formation actuelle ne clone aeac-2026. La Formation 5 sera le premier contact réel des nouveaux avec le dépôt.

---

## 6. Esquisse pour la Formation 5 et questions restantes

**Fil conducteur proposé** (dans le style des rails : bloc avant de commencer, jalons « tu as réussi si », table « quand ça casse ») :

1. Le dépôt vu de haut : `ARCHITECTURE.md`, schéma Jetson/GCS, qui tourne où. Jalon : dessiner le schéma de mémoire.
2. Git en trois règles : `main` = ce qui vole, branche + PR, `ensure_submodules.sh` au clone. Jalon : PR ouverte sur une branche perso. Pas plus.
3. Infra : Makefile (`C=`, `help`, `print-vars`), compose, Dockerfile drone vs GCS, systemd. Jalon : `make shell C=water` et `ros2 topic list` non vide.
4. Workspaces et paquets : `pkgs.txt`, `link_ws.sh`, sous-module vs local, `package.xml` comme contrat. Jalon : ajouter un paquet à un workspace.
5. Interfaces et nommage : `custom_interfaces`, `topics.py`, `/aeac/internal|external`, listes `allow` Zenoh. Exercice : retrouver un câblage mort à partir de `ros2 topic info` (garder un des quatre de la table 3.3 comme exercice, corriger les trois autres).
6. Une mission de bout en bout en simulation : SITL + `target_detection_mock` + `rc_simulator`, `water_mission.launch.py`, `auto_approach.py`, heartbeats, `procédure.md`. Jalon : la machine à états passe par tous ses états sans drone.
7. Config par mission : changer le YAML pour un autre site, relancer. Jalon : les coordonnées de scène viennent du YAML, pas du code.

**Questions restantes à trancher :**
- Sort de `left-right-payload`.
- Emplacement des paquets dédupliqués (option a ou b du point 4.2.5).
- Forme du template 2027 (les trois questions ouvertes du point 4.2.8).
- Règle de langue pour le code, les logs et les commits.
- Quel câblage mort garder comme exercice.

---

## 7. Commentaires de Colin (18 septembre 2026) et décisions

Consignés tels quels après la première version de la revue, avec la décision retenue.

| Commentaire | Décision appliquée |
|---|---|
| « Le nœud de terminaison a jamais été utilisé. » | `TerminationSystem` requalifié en code mort (3.4, 3.5), retiré du critère sécurité et de l'esquisse de formation. |
| « La sim était partie via Mission Planner ou Gazebo, tu veux quoi par : mocks utiles mais éparpillés ; aucun test réel ; templates de test jamais lancés. » | Critère 6 reformulé : SITL couvre l'autopilote, le manque est un launch `sim` qui assemble les mocks ROS existants (précision ajoutée sous la table de la section 0). « Aucun test réel » retiré. |
| « Je veux vraiment pas overwhelm les nouveaux avec toutes les bonnes pratiques git plus avancées. » | Section 3.1 réduite à trois règles enseignées ; conventions de commit, tags, CI, CONTRIBUTING déplacés en « pour les leads seulement ». Module git de l'esquisse réduit. |
| « Je suis okay avec des Dockerfiles presque identiques mais presque différents. » | Recommandation « un seul Dockerfile » retirée. |
| « Dev évité c'est pas très grave, mais on va uniformiser à long terme. » | Utilisateur `dev` / root dans le conteneur : rétrogradé en « long terme » (3.2, 4.2.6). |
| « `privileged: true` + `ipc: host` sur le conteneur de dev : c'est okay. » | Point retiré. |
| « Uniformiser les noms est effectivement essentiel. » | Section 3.3 marquée priorité absolue ; solution minimale `topics.py` en 4.2.3. |
| « `main` est effectivement à ne pas utiliser. Oui fusionner mission 2. » | Quick win 1 confirmé ; `main` = ce qui vole. |
| 4.2.1 « Non, un Dockerfile par drone et pour la GCS. » | Réécrit : un par machine, nommés par machine. |
| 4.2.2 « Explique plus, je suis ouvert. » | Mécanismes A et B détaillés avec conséquences et recommandation. |
| 4.2.3 « Oui bonne idée, mais faut vraiment le garder super simple et direct pour les nouveaux. » | Version minimale : un fichier de constantes plates, exemple inclus. |
| 4.2.4 « Oui config par mission. » | Confirmé, contenu précisé. |
| 4.2.5 « Je suis d'accord, mais je suis pas sûr de ton `mission_common`. » | `mission_common` retiré ; deux options proposées (sous-modules dans `packages/`, ou fusion dans `tools`). |
| 4.2.6 « Non, pas de tests. » | Recommandations de tests et de CI retirées ; les templates `test/` sont à supprimer. |
| 4.2.7 « Non. » | Découpage de `position_system.py` retiré. |
| 4.2.8 « Pas très important, mais oui `main` = ce qui vole. » | Convention de commits retirée ; seule la règle `main` reste. |
| 4.2.9 « Oui faut faire un template, je suis pas sûr comment, faudra plus brainstormer. » | Gardé comme chantier ouvert avec trois questions de départ. |
| « Ajuste la cohérence des formations. » | Cinq passages corrigés dans Formations-Controle (section 5). |
