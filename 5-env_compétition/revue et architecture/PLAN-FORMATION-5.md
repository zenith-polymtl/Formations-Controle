# Plan de la formation 5 : l'environnement de compétition

*Document de travail, 21 septembre 2026. Ce n'est pas la formation : c'est sa structure, le contenu à y mettre et les questions à trancher avant la rédaction. Sources : le narratif de visite du dépôt dicté par Colin le 22 septembre 2026, le plan d'architecture V3 (propositions P25 et P26, section 12), le squelette `mission-template/`, la revue pédagogique d'aeac-2026 (section 6) et le plan d'apprentissage (bloc B5, rattaché à l'objectif 5 du 21 novembre).*

*Périmètre volontairement réduit. Les services systemd, l'architecture réseau, Zenoh et l'intégration d'un capteur spécialisé (la ZED) sont dans la formation 6. La vision aura sa propre formation. Les rôles humains et le déroulé d'une compétition sont dans la formation d'introduction aux drones. Ici tout cela est nommé en une phrase, jamais expliqué.*

*Deux contraintes de cadrage, tranchées le 22 septembre. La formation vise à faire reconnaître les éléments de l'environnement, pas à faire comprendre ce qui se passe le jour de la compétition. Et elle doit rester utilisable telle quelle par une recrue qui n'a pas encore fait la formation 6, même si celle-ci suit de peu : on doit pouvoir la finir sans rien apprendre de réseautique.*

*Format : documents écrits, faits en autonomie, comme les formations 2 et 3.*

---

## 0. Ce que la formation doit accomplir

### Le public

Une recrue qui a fait les formations 2 et 3 : elle a WSL, Docker et Make, elle a écrit une node ROS 2 avec un launch et une cible Make, elle a fait décoller le drone simulé avec mavros. Elle n'a jamais vu le dépôt de compétition, n'a pas de Jetson, pas de ZED, pas de manette. Elle va bientôt recevoir une tâche de mission dans aeac-2027 et doit pouvoir la faire sans qu'un lead lui explique le dépôt de vive voix.

### Le résultat attendu

À la fin, la recrue est capable de :

- Dessiner de mémoire qui tourne où (poste WSL, Jetson, portable GCS) et dire ce qui est pour le drone et ce qui est pour le développement.
- Cloner un dépôt de mission et le faire tourner seule : `make init`, `make build C=`, `make dev`.
- Lancer une mission en simulation dans trois terminaux et suivre ses états dans `ros2 topic echo`.
- Changer un waypoint ou un seuil sans toucher au code, dans le bon fichier de `config/`.
- Ajouter un nœud à une mission en respectant les règles du dépôt (`topics.py`, constantes de `custom_interfaces`, `package.xml`, `make link`, `make check`) et ouvrir une PR.
- Réciter les trois règles git et les deux règles de sécurité.

### Pourquoi le dépôt a cette forme

À dire en ouverture, avant toute commande, parce que c'est ce qui rend le reste lisible. aeac-2027, comme aeac-2026, existe pour supporter la diversification : plusieurs paquets à faire vivre ensemble, et du modulaire partout, plusieurs opérateurs, plusieurs ordinateurs, plusieurs conteneurs, plusieurs workspaces, plusieurs missions. Chaque dossier du dépôt est la réponse à un de ces « plusieurs ».

C'est aussi ce qui explique que la recrue retrouve des objets connus, mais au pluriel. Le Dockerfile unique des formations précédentes est devenu un dossier `docker/` avec un fichier par rôle. Le compose unique est devenu un dossier `compose/` avec un fichier par chose à lancer. Le Makefile qui coordonnait deux commandes en coordonne maintenant trois régimes. Rien de nouveau comme outil : c'est la même boîte, rangée pour plusieurs.

### Le fil conducteur

**Une mission démo, suivie du clone jusqu'à la PR.** La formation fournit `demo_ws/` (P26) : quatre états `IDLE`, `GOTO`, `ACT`, `RETURN`, un GO externe, un waypoint lu dans le YAML de site, une action factice, un retour ; une centaine de lignes. La recrue copie `mission-template/`, y dépose `demo_ws`, lie les paquets partagés, simule, modifie la config, puis ajoute son propre nœud. Chaque document se termine sur quelque chose qui tourne à l'écran.

Le template est celui de la formation, pas aeac-2027 : la recrue travaille sur une copie locale qu'elle peut casser. aeac-2027 ne voit jamais la démo.

Avant ce fil, une visite guidée du dépôt (5.1, section 2) : une dizaine de minutes, dossier par dossier, sans commande. C'est la carte qu'on regarde avant de marcher, pour que la recrue sache où elle est quand une commande échouera.

### Ce qui distingue cette formation des autres

Les formations 2 et 3 apprenaient des outils. Ici l'outil est connu, c'est la structure qui est nouvelle, et la tentation est de tout expliquer. Le risque est l'inverse de la formation 9 : non pas la lecture passive, mais la noyade dans les concepts. D'où trois choix :

- **Un concept n'apparaît que quand la recrue en a besoin pour la prochaine commande.** Les sous-modules arrivent quand `make status` les montre, pas avant. Zenoh arrive en une phrase quand un topic `external` apparaît, et s'arrête là.
- **Chaque section est un geste, pas une notion.** « Ajouter un paquet partagé » est `make link`, pas une explication des symlinks.
- **Ce qui est pour les leads est marqué comme tel et sauté.** La recette « créer un dépôt de mission », `make bump`, `make deploy` : lus une fois, jamais pratiqués ici.

---

## 1. Découpage proposé

Trois documents, dans le style des formations 2 et 3 (bloc « avant de commencer », jalons « tu as réussi si », table « quand ça casse »).

| Document | Sujet | Réussite | Durée estimée |
|---|---|---|---|
| 5.1 Le dépôt vu de haut | Qui tourne où, la visite du dépôt dossier par dossier, le Makefile en trois sections, clone et première construction, les règles | Le schéma dessiné de mémoire ; les sept dossiers nommés écran éteint ; `make dev` puis un topic du sol qui s'affiche | 1 h 45 |
| 5.2 Une mission en simulation | `demo_ws`, `make sim C=demo`, trois terminaux, le paramètre `sim`, la config par mission, site et drone, la démarche de débogage | La machine à états passe par ses quatre états sans drone ; un waypoint changé dans le YAML ; trois pannes diagnostiquées | 2 h 30 |
| 5.3 Projet : ajouter un nœud | Un nœud de plus dans la démo, les règles de code, `make check`, rappel git, branche et PR | Une PR ouverte, `make check` vert, le nouveau topic visible dans un second terminal | 2 h |

Total : environ 6 h 15 pour la recrue, plus une annexe de vingt minutes réservée aux leads (section 5). Rédaction : 4 h pour `demo_ws` (P26) plus environ 6 h pour les trois documents ; voir la question 2.

---

## 2. Document 5.1 : le dépôt vu de haut

### Objectifs

- Nommer les trois machines (poste WSL, Jetson, portable GCS), leurs régimes (développement, simulation, test, déploiement, vol) et ce qui tourne sur chacune.
- Nommer chaque dossier du dépôt et dire à quel « plusieurs » il répond.
- Lire le Makefile en trois sections et savoir laquelle la concerne.
- Cloner, initialiser et construire un dépôt de mission sans aide.
- Réciter les règles du dépôt.

### Bloc « Avant de commencer »

- Durée : 1 h 45, dont une dizaine de minutes de visite du dépôt et une quinzaine de construction Docker.
- Prérequis : formations 2 et 3 faites, et l'introduction aux drones pour les rôles dans l'équipe. La formation 4 (Gazebo) n'est pas nécessaire, le simulateur est celui de Mission Planner.
- À la fin : le conteneur de développement ouvert, le workspace `gcs_ws` construit, le heartbeat du sol visible dans `ros2 topic echo`.
- Aide : Discord, salon Contrôle, fil « Formations et Questions ».
- À poster à la fin : une photo du schéma dessiné à la main et une capture de `make status`.

### 1. Lire ARCHITECTURE.md, puis fermer l'écran

La première demi-heure se passe sur une seule page : `ARCHITECTURE.md` du template. Le tableau « qui tourne où » et le schéma « ce qui traverse la radio ». Exercice : fermer le fichier et redessiner sur papier les trois machines, ce qui tourne dessus, et la flèche unique qui traverse la radio. Jalon : le dessin.

Ce qu'on dit du réseau ici, et rien de plus : le drone et le sol sont deux mondes ROS séparés, un topic nommé `/aeac/external/...` passe de l'un à l'autre, un topic `/aeac/internal/...` reste sur le drone. Comment ça passe est la formation 6.

Systemd n'est pas nommé ici : il arrive à la section suivante, avec le dossier qui le contient.

### 2. La visite du dépôt, dossier par dossier

Une dizaine de minutes, `ls` à la racine, un dossier à la fois, une ou deux phrases chacun. Pas de commande, pas d'exercice : on regarde la carte. À chaque ligne, redire à quel « plusieurs » le dossier répond.

| Dossier | Ce qu'on en dit, et rien de plus |
|---|---|
| `docker/` | Plusieurs conteneurs plutôt qu'un seul, parce que les besoins diffèrent : un fichier par rôle, `drone`, `gcs`, `mavros` (le lien avec l'autopilote, donc la communication), `vision` (qui n'a pas du tout les mêmes dépendances, GPU et modèles). L'en-tête de chaque fichier dit ce qui change par rapport aux autres. |
| `compose/` | Ce qu'on lance, une fois les images construites. `drone.yml` lance le launch de la mission, `mavros.yml` le lien avec l'autopilote, `vision.yml` la perception, `zed.yml` la caméra, `zenoh-air.yml` et `zenoh-ground.yml` la radio, `sim.yml` l'environnement de simulation. `dev.yml` est le polyvalent : il monte tout le dépôt et supporte plusieurs configurations, c'est le seul que la recrue utilise pendant la formation. |
| `config/` | Les réglages sortis du code, rangés selon ce qui les fait changer : la mission, le site, le drone. Deux formats, pour une raison simple : le YAML est le format natif des paramètres ROS 2 (sites, mavros, zed), le JSON5 celui de Zenoh (drones, radio). On le dit en une phrase et on passe. Détaillé en 5.2. |
| `packages/` | Les paquets partagés. Chacun est un dépôt à part, rattaché ici en sous-module git : un dépôt dans un dépôt, ce qui permet au même paquet de servir dans plusieurs dépôts de mission. On y revient à la section 4, quand `make status` les affiche. |
| `scripts/` | Les petits programmes utiles, Python ou bash, qui aident à vérifier ou à préparer l'environnement de compétition. La règle est simple : un script qui a resservi une deuxième fois finit ici. Section volontairement diverse, elle grossit d'année en année. Le seul utilisé dans la formation est `check.py`, par `make check` (5.3). |
| `systemd/` | Important, même si on ne le pratique pas ici. Un service systemd est un petit emballage qui lance une commande, le plus souvent un `docker compose`, au démarrage de l'ordinateur. Sur la Jetson il y en a un par brique : la caméra ZED, mavros, la radio, la vision, la mission. C'est ce qui fait qu'au jour J on met sous tension et que tout est déjà parti, sans personne au clavier. La formation 6 les ouvre. |
| `workspaces/` | Là où sont les missions : une mission, un workspace. Deux exceptions, `vision_ws`, qui a ses propres fichiers et ne se construit que sur la Jetson, et `gcs_ws`, qui est le sol seulement. |
| `README.md`, `ARCHITECTURE.md`, `procédure.md`, `NOTES.md` | Les quatre documents du dépôt : par où commencer, la carte, le jour J, le carnet. Les deux premiers sont lus dans cette formation, les deux autres sont montrés. |
| `Makefile` | Ce qui coordonne tout le reste, comme dans les formations précédentes. Section suivante. |

Jalon : écran éteint, la recrue nomme les sept dossiers et dit en une phrase ce que chacun contient. C'est la seule chose de 5.1 qu'on redemande au début de 5.2.

### 3. Le Makefile en trois sections

`make help`. Les trois sections correspondent aux trois régimes du tableau : développement et simulation (le poste), test sur véhicule (la Jetson, à la main), déploiement (la Jetson, au boot, leads). La recrue ne touche qu'à la première pendant toute la formation.

Les trois variables et ce qu'elles choisissent : `C=` la mission donc le workspace, `IMG=` le conteneur, `DRONE=` le fichier de config du sol. `make print-vars` pour voir ce que ça donne. Différence avec la formation 3.4 : le Makefile n'est plus un raccourci pour un compose, c'est l'interface du dépôt, et chaque cible dit dans quel régime on est.

### 4. Cloner, initialiser, construire

Dans l'ordre du README : `git clone --recurse-submodules`, `make init`, `make status`, `make build C=gcs`, `make dev`. À chaque commande, une phrase sur ce qu'elle a fait, lisible dans sa sortie. C'est ici que les sous-modules apparaissent, par `make status`, avec les trois phrases d'`ARCHITECTURE.md` et pas une de plus : on clone avec `--recurse-submodules`, `make init` rattrape si on a oublié, si `make status` dit « modifié localement » on demande à un lead.

C'est le moment où la visite devient concrète : `docker/` et `compose/` viennent de servir à `make build` et `make dev`, `packages/` vient d'apparaître dans `make status`. Deux précisions à ajouter ici, pas avant :

- Le conteneur de développement monte tout le dépôt dans `/aeac`, c'est pour ça qu'on peut y construire n'importe quel workspace.
- Un workspace de mission contient ses propres paquets et des liens vers les paquets partagés de `packages/`. `gcs_ws` est le workspace du sol et aussi celui où on développe.

Ce qu'on demande de comprendre des sous-modules, et pas plus : que `packages/` contient des dépôts à part, qu'on sait donc retrouver où vit un bout de code quand on tombe sur un import (`tools.topics` est dans `packages/tools/`, pas dans la mission), que le modifier ici modifie un autre dépôt et concerne d'autres missions, et qu'on sait lire les trois états de `make status`. Naviguer dans l'architecture, pas l'administrer : l'administration est dans l'annexe des leads.

Jalon : dans le conteneur, `ros2 launch gcs_bringup base.launch.py` dans un terminal, `ros2 topic echo` du heartbeat dans un autre (`make shell`).

### 5. Les règles, en une page

Les six règles du README, lues à voix haute. Deux sont à retenir avant de coder quoi que ce soit :

- Le code de mission n'arme jamais et ne change jamais de mode. C'est le pilote. Les seuls nœuds qui le font sont les `*_test` de `sim_mocks`, sous `sim:=true`.
- `main` = ce qui vole. Branche, PR, un lead fusionne. `make check` avant la PR.

Et où écrire : `NOTES.md` pour ce qu'on apprend, `procédure.md` pour le jour J (lu, pas pratiqué : la recrue n'a pas de drone).

### Quand ça casse (5.1)

| Symptôme | Cause probable | Remède |
|---|---|---|
| `make build` dit qu'un paquet manque | Sous-module vide | `make status`, puis `make init` |
| `ros2 topic list` vide dans le conteneur | `ROS_DOMAIN_ID` différent entre les deux terminaux | Les deux terminaux dans le même conteneur (`make shell`) |
| Fichiers appartenant à root | Les conteneurs tournent en root | `sudo chown -R $USER:$USER .` |
| `make` inconnu sous WSL | Paquet absent | `sudo apt install make` (à ajouter à la formation 2, voir la question 5) |

---

## 3. Document 5.2 : une mission en simulation

### Objectifs

- Installer `demo_ws` dans un template copié, lier les paquets partagés, construire.
- Lancer la mission en simulation dans trois terminaux et suivre ses états.
- Comprendre le paramètre `sim` et pourquoi le launch est le même en simulation et en vol.
- Savoir où va un réglage : mission, site ou drone.
- Enregistrer un rosbag.
- Chercher une panne dans l'ordre : conteneur, nœud, donnée.

### Bloc « Avant de commencer »

- Durée : 2 h 30.
- Prérequis : 5.1, et le SITL de Mission Planner qui démarre (formation 1). On commence par se redemander les sept dossiers, deux minutes, à l'écrit sur une feuille.
- À la fin : la machine à états de la démo est passée par `IDLE`, `GOTO`, `ACT`, `RETURN` sans drone, et le waypoint vient du YAML de site.
- À poster à la fin : une capture de `ros2 topic echo` de l'état avec les quatre transitions, le diff du YAML, et les trois causes trouvées à l'exercice de débogage.

### 1. Poser la démo

`demo_ws/` est fourni dans le dossier de la formation. Gestes : copier dans `workspaces/`, `make link C=demo PKG=tools`, `make link C=demo PKG=custom_interfaces`, `make build C=demo`. Puis lire `demo_bringup/launch/mission.launch.py` et le nœud de mission (une centaine de lignes) avec trois questions guidées : où sont les noms de topics (dans `topics.py`, jamais dans le nœud), où sont les états (constantes de `custom_interfaces`), où est le waypoint (nulle part dans le code).

### 2. Trois terminaux

Le cœur de la formation (P25). Terminal 1 : `make sim C=demo`. Terminal 2 : `make shell IMG=sim` puis `ros2 run sim_mocks rc_simulator`. Terminal 3 : `make shell IMG=sim` puis `ros2 topic echo` de l'état de la mission.

Déroulé : SITL prêt dans Mission Planner, `takeoff_test` pour décoller (il refuse sans `sim:=true`, c'est voulu), un interrupteur du `rc_simulator` pour le GO, et les quatre états défilent. Jalon : la capture des quatre transitions.

Ce qu'on explique ici, une fois le jalon atteint : `sim:=true` ne fait qu'une chose, passer un paramètre `sim` aux nœuds qui touchent au matériel ; ils entourent leur seul appel matériel d'un `if not self.sim`. Le launch de vol et le launch de simulation sont le même fichier. Les mocks se lancent à la main et aucun launch de mission ne les inclut.

Lecture de `sim_mocks/README.md` : les trois mocks, ce que chacun remplace, la règle pour en écrire un.

### 3. Mission, site, drone

Trois fichiers, trois questions : est-ce que ça change avec la mission (`config/demo.yaml` : gains, seuils, interrupteurs), avec le terrain (`config/sites/sim.yaml` : coordonnées), avec le drone (`config/drones/hexa.json5` : adresses, formation 6) ? Exercice : déplacer le waypoint de cent mètres dans `sites/sim.yaml`, relancer, voir le drone aller ailleurs dans Mission Planner. Puis créer `sites/polytechnique.yaml` et relancer avec `site:=polytechnique`. Jalon : le diff.

### 4. Enregistrer

`make bag` dans un quatrième terminal pendant un tour de mission, puis `ros2 bag info` sur le résultat. Une phrase sur ce qui est enregistré (`/aeac/*` et les topics mavros utiles) et pourquoi on le fait à chaque vol.

### 5. Quand ça ne marche pas : la démarche

Une demi-heure, après le rosbag, pendant que la simulation tourne encore. Ce n'est pas une liste de pannes (elle est dans la table ci-dessous) mais l'ordre dans lequel on cherche. Trois étages, et la question qui fait passer au suivant :

1. **Est-ce que le conteneur tourne ?** `docker ps`, puis `docker compose -f compose/sim.yml logs -f`. Si le conteneur est sorti, le problème est avant ROS et les commandes ROS ne diront rien.
2. **Est-ce que le nœud tourne ?** `make shell`, `ros2 node list`, `ros2 topic list`. Un nœud absent est une erreur au lancement : on remonte aux logs du launch.
3. **Est-ce que la donnée circule ?** `ros2 topic hz`, `ros2 topic echo`, `ros2 topic info -v` pour le QoS. Un topic listé mais muet, c'est presque toujours un émetteur mort ou un QoS incompatible.

Exercice : trois pannes préfabriquées, fournies dans le dossier de la formation sous forme de patchs à appliquer sans les lire (un nom de topic changé dans la config, un conteneur qui refuse de démarrer faute de construction, un nœud lancé sur un autre `ROS_DOMAIN_ID`). La recrue les diagnostique dans l'ordre ci-dessus et note dans `NOTES.md` ce qui l'a mise sur la piste. Jalon : les trois causes, et la ligne de `NOTES.md`.

Une phrase à dire ici et pas avant : sur le drone, ces mêmes trois étages servent le jour J, avec un étage de plus au-dessus, parce que le lancement vient de systemd et pas de nous. La formation 6 ajoute cet étage.

### Quand ça casse (5.2)

| Symptôme | Cause probable | Remède |
|---|---|---|
| `mavros-sim` ne se connecte pas | SITL non lancé, ou `SITL_HOST` faux | Mission Planner d'abord ; `make print-vars` ; formation 3.3 |
| `takeoff_test` refuse de démarrer | Lancé sans `-p sim:=true` | C'est le comportement voulu |
| Le GO ne passe pas | `rc_simulator` n'a pas le focus clavier | Cliquer dans son terminal |
| L'état ne change pas après le GO | Drone pas en `GUIDED` ou pas armé | `takeoff_test` d'abord, puis vérifier `/mavros/state` |
| Le waypoint n'a pas bougé | Mauvais fichier modifié, ou `site:=` oublié | `ros2 param get` sur le nœud |
| Rien ne répond et on ne sait pas par où commencer | C'est le cas normal | Les trois étages de la section 5, dans l'ordre |

---

## 4. Document 5.3 : projet, ajouter un nœud à la démo

### Objectifs

- Ajouter un nœud à un workspace de mission en respectant les règles de code.
- Déclarer un nouveau topic au bon endroit et le rendre externe ou interne en le nommant.
- Passer `make check`, ouvrir une PR en appliquant le rappel git.

### Bloc « Avant de commencer »

- Durée : 2 h.
- Prérequis : 5.2.
- À la fin : une PR ouverte (ou un patch posté, voir la question 4), `make check` vert.
- À poster à la fin : le lien de la PR ou le patch, et une capture du nouveau topic vu depuis un second terminal.

### 1. Le cahier des charges

Un nœud `mission_monitor` dans `demo_ws/src/demo_monitor/` : il s'abonne à l'état de la mission et à `/mavros/battery`, et publie un résumé sur un topic externe (état courant, tension, temps passé dans l'état) à 1 Hz. Il n'arme rien, ne change rien, il regarde. C'est le nœud le plus simple qui oblige à toucher à tout : un paquet, un `package.xml`, une constante dans `topics.py`, un launch, la config.

### 2. Le squelette et les règles

Le squelette est fourni comme en 3.4. Les règles qu'il illustre, chacune avec la ligne qui la respecte :

- Le nom du topic vient de `topics.py` (une ligne ajoutée dans `tools`, sur la copie locale du sous-module ; on explique que dans la vraie vie c'est une PR dans `tools` faite avec un lead).
- L'état est comparé à une constante de `custom_interfaces`, pas à une chaîne.
- Pas de `time.sleep` dans un callback : un timer à 1 Hz.
- `package.xml` déclare `rclpy`, `mavros_msgs`, `tools`, `custom_interfaces`.
- Le résumé est `external` parce que le sol veut le voir ; le préfixe suffit, rien d'autre à faire (la formation 6 montre ce qui se passe derrière).
- Logs en français, `INFO` pour les événements, jamais du périodique.

### 3. Brancher et vérifier

Ajouter le nœud au launch de la démo, un paramètre dans `config/demo.yaml` (le seuil de tension qui déclenche un `WARN`), `make build C=demo`, `make sim C=demo`, le topic dans un second terminal. Puis `make check` : lire sa sortie, corriger ce qu'il relève (maintainer, licence, description du `package.xml` ; le squelette les oublie exprès).

### 4. Rappel git, puis branche et PR

Git a été vu rapidement en B0 et n'est pas réenseigné ici : quinze minutes de rappel, appliquées tout de suite au travail qu'on vient de faire. Les commandes dans l'ordre où on les tape : `git status`, `git switch -c prenom/monitor`, `git add -p`, `git commit`, `git push -u origin`, puis la PR dans le navigateur.

Trois règles et rien d'autre : une branche par tâche, un message de commit en anglais sur une ligne, `main` ne se pousse jamais directement. `make check` avant d'ouvrir la PR. Le lead qui relit vérifie la liste de la section 2.

### Quand ça casse (5.3)

| Symptôme | Cause probable | Remède |
|---|---|---|
| `ImportError: tools.topics` | Lien manquant ou workspace pas resourcé | `make link C=demo PKG=tools`, rebuild, nouveau shell |
| `make check` rouge sur le `package.xml` | Métadonnées manquantes | Les remplir, c'est l'exercice |
| Le topic apparaît mais rien ne sort | Callback jamais appelée : QoS de `/mavros/battery` | `ros2 topic info -v`, formation 3.3 |
| Le topic s'appelle autrement que prévu | Littéral dans le nœud au lieu de `topics.py` | `grep` du nom dans `demo_ws` |

---

## 5. Annexe pour les leads : créer et faire évoluer l'environnement

Un document court, clairement marqué « leads », à la fin du dossier de la formation. La recrue sait qu'il existe et ne le fait pas ; elle reste l'utilisateur principal de la formation. L'annexe répond à la question que personne ne documente et qui se repose chaque année : comment on fabrique un environnement de mission, et pas seulement comment on l'habite.

Contenu, en gestes plutôt qu'en explications :

- **Créer un dépôt de mission** à partir de `mission-template` : cloner le template, renommer, rattacher les sous-modules de `packages/`, premier commit, droits GitHub. C'est la recette du README, reprise ici avec ce qui manque dedans.
- **Ajouter une mission** au dépôt : créer `workspaces/<nom>_ws`, son paquet `bringup`, son launch, sa config, lier les paquets partagés, valider avec `make check`.
- **Ajouter un paquet partagé** : quand un bout de code passe d'une mission à `packages/`, comment on en fait un dépôt, comment on l'ajoute en sous-module, et comment on prévient les autres dépôts qui le suivent.
- **Ajouter un conteneur** : un fichier dans `docker/`, un fichier dans `compose/`, ce qu'on met dans l'en-tête pour que le suivant comprenne ce qui diffère.
- **Ajouter un service au boot** : le fichier dans `systemd/`, `install.md`, l'ordre de dépendance. Le détail est dans la formation 6, ici on montre seulement où ça se met.
- **Faire évoluer** : `make bump`, `make deploy`, la section « pour les leads » d'`ARCHITECTURE.md`.

Vingt minutes de lecture. Ce n'est pas un exercice, c'est une recette, mais elle doit être écrite assez précisément pour qu'un lead de 2028 s'en serve sans nous.

## 6. Ce qui est lu mais pas pratiqué

Une page de fin, « pour plus tard », pour que la carte soit complète sans alourdir :

- L'annexe des leads ci-dessus, à parcourir une fois pour savoir ce qu'elle contient.
- `procédure.md`, à lire une fois pour savoir qu'elle existe.
- La formation 6 : réseau, Zenoh, services, capteurs.
- La formation vision, à venir : `vision_ws`, les modèles, la ZED.

---

## 7. Matériel à produire

- `demo_ws/` : `demo_bringup` (launch, `config/demo.yaml` à copier dans `config/`), `demo_mission` (le nœud, une centaine de lignes), `README.md` de deux paragraphes. 4 h (P26).
- Le squelette et la solution de `demo_monitor` (5.3).
- Un `config/sites/polytechnique.yaml` d'exemple (coordonnées du terrain habituel).
- Les captures : `ls` à la racine du dépôt, `make help`, `make status`, les quatre transitions, `ros2 bag info`.
- Les trois patchs de pannes préfabriquées de 5.2, avec leur solution dans un fichier à part.
- L'annexe des leads (section 5), écrite avec un lead qui a fait la manœuvre au moins une fois.
- Une ligne dans `Control-Formations/README.md` et dans `0-prerequis` pour le parcours.

---

## 8. Décisions et questions

### Tranché le 22 septembre 2026

- **Portée.** Faire reconnaître les éléments de l'environnement, pas le déroulé de la compétition.
- **Format.** Documents écrits, en autonomie, comme les formations 2 et 3. Pas de capsule vidéo pour la visite du dépôt.
- **Indépendance.** La 5 tient sans la 6, même si la 6 suit de peu. On doit pouvoir la finir sans réseautique.
- **Leads.** Une annexe sur la création d'un environnement (section 5), la recrue restant l'utilisateur principal.
- **Sous-modules.** Assez pour comprendre les interactions et naviguer dans le dépôt. L'administration est dans l'annexe.
- **Vision.** Formation séparée, hors périmètre ici.
- **Débogage.** Une demi-heure méthodique en fin de 5.2, avec trois pannes préfabriquées.
- **Rôles humains.** Formation d'introduction aux drones, pas ici.
- **Git.** Rappel bref et application immédiate en 5.3, la base venant de B0.
- **Formats de config.** YAML natif ROS 2, JSON5 natif Zenoh, une phrase et on passe.
- **`scripts/`.** Dépôt de tout script Python ou bash généralement utile.
- **Validation.** Jalons postés sur Discord ou annoncés au lead.

### Reste à trancher avant la rédaction

1. **Dépendance à l'étape 1 de la V3.** `topics.py` et les constantes d'état n'existent pas encore dans `tools` et `custom_interfaces`. 5.2 et 5.3 en dépendent. Soit on restructure les dépôts partagés d'abord (ordre de la V3), soit la démo embarque provisoirement ses propres constantes et on la corrige après. Recommandation : restructurer d'abord, la formation doit montrer le vrai geste.
2. **Budget de rédaction.** Le plan d'apprentissage budgète environ 5 h pour B5 en plus de l'objectif 5. Ici on arrive à 4 h de démo plus environ 7 h de documents, annexe des leads et pannes préfabriquées comprises. Soit on accepte 11 h, soit 5.3 devient un « défi » d'une page sans squelette.
3. **Le heartbeat comme premier topic (5.1).** Le jalon suppose que `gcs_bringup/base.launch.py` lance `tools gcs_heartbeat` et que ça tourne sans mavros. À vérifier sur le `tools` restructuré.
4. **PR sur quoi (5.3).** La recrue travaille sur une copie locale non poussée. Options : un dépôt `formation-5-demo` par cohorte sur GitHub où chacun pousse sa branche (le lead relit une vraie PR), ou un patch posté sur Discord. Recommandation : le dépôt par cohorte, c'est le geste réel.
5. **`make` absent sous WSL.** Constaté sur le poste de Colin. À ajouter à la formation 2, section 2.8, plutôt qu'ici.
6. **Formation 4.** Vide aujourd'hui. Soit elle devient l'annexe Gazebo, soit la numérotation glisse. La formation 5 ne doit pas l'attendre.
7. **Le SITL et le site.** `sites/sim.yaml` pointe sur le domicile par défaut du SITL (Canberra). L'exercice « déplacer le waypoint » suppose que le SITL accepte un waypoint à cent mètres ; à essayer avant d'écrire.
8. **Contenu de `scripts/`.** La section est décrite comme le dépôt des scripts utiles, mais elle ne contient que `check.py`. Les scripts de 2026 qui méritent d'y être rapatriés sont à recenser, sinon la visite décrit un dossier vide.
9. **Quand écrire la formation vision.** Elle est maintenant citée dans deux documents. Il faut au moins un numéro de bloc et une place dans le parcours avant la rédaction de la 5.
10. **Révision.** Le plan d'apprentissage nomme Haithem Tebib et Nour Karoui comme réviseurs de l'objectif 5. La démo et 5.3 gagneraient à être testés par une recrue de la cohorte d'automne avant révision.
