# Tâche 3 : matériel d'exercice de la formation 5 (pannes préfabriquées et projet `demo_monitor`)

Contexte : la formation 5 du club Zenith fait tourner une mission démo (`demo_ws`, tâche 2) dans le dépôt de mission (structure de `C:\Users\colin\Zenith\aeac-2027`). Le document 5.2 se termine par un exercice de débogage à trois étages (conteneur, nœud, donnée) sur trois pannes préfabriquées. Le document 5.3 est un projet : ajouter un nœud `mission_monitor` à la démo, en partant d'un squelette qui oublie exprès des métadonnées.

Emplacement : `C:\Users\colin\Zenith\Control-Formations\5-env_compétition\` (dépôt git Control-Formations, branche `prep_formation_5_et_aeac2027`). À lire d'abord : `demo_ws/` complet (tâche 2, déjà en place), et dans `aeac-2027` : `ARCHITECTURE.md`, `compose/sim.yml`, `scripts/check.py` (ce qu'il détecte : mainteneur `todo`, licence vide/TODO, description vide, dossier `test/`), `packages/tools/tools/topics.py`, `packages/custom_interfaces/msg/MissionState.msg`, `config/README.md`, `config/sites/sim.yaml`. Pour le style de solution : `C:\Users\colin\Zenith\Control-Formations\3-ros2\solutions\`.

## A. `pannes/` : trois patchs et leurs solutions

Structure :
```
pannes/
  README.md            comment appliquer un patch sans le lire, comment le retirer (git apply / git apply -R depuis la racine du clone), et l'ordre de recherche en trois étages (une ligne chacun)
  panne-1.patch
  panne-2.patch
  panne-3.patch
  SOLUTIONS.md         pour les leads : la cause de chaque panne, l'étage où on la trouve, la commande qui la révèle, la ligne du patch
```

Les patchs sont au format `git diff` unifié, applicables depuis la racine d'un clone où `demo_ws` a été copié dans `workspaces/` et `demo.yaml` dans `config/`, avec `git apply pannes/panne-N.patch`. Génère-les réellement : copie `demo_ws`, `compose/sim.yml` et `config/` d'aeac-2027 dans un dossier de travail du scratchpad, initialise un git, commet, applique la modification, `git diff > panne-N.patch`, puis vérifie `git apply --check` et `git apply -R --check`. Le nom de fichier dans le patch doit être le chemin dans le clone (`workspaces/demo_ws/...`, `compose/sim.yml`, `config/demo.yaml`).

Les trois pannes, une par étage :
- **Étage donnée** : dans `config/demo.yaml`, `rc.go_channel` passe de 7 à 12. Tout tourne, l'état reste `IDLE`, le GO ne passe jamais. Révélé par `ros2 topic echo /mavros/rc/in` (le canal 7 bouge) et `ros2 param get /demo_mission rc.go_channel`.
- **Étage conteneur** : dans `compose/sim.yml`, le `working_dir` du service `sim` passe à `/aeac/workspaces/${C:-gcs}_wss` (un `s` de trop). Le conteneur `sim` sort immédiatement ; `docker ps` ne le montre plus, `docker compose -f compose/sim.yml logs` dit pourquoi.
- **Étage nœud** : dans `compose/sim.yml`, le service `mavros-sim` reçoit `ROS_DOMAIN_ID=4` au lieu de 3. Les deux conteneurs tournent, le nœud de mission tourne, mais `ros2 topic list` depuis `make shell IMG=sim` ne montre aucun `/mavros/*`. Révélé par `docker compose -f compose/sim.yml exec mavros-sim env | grep ROS_DOMAIN`.

Numérote-les 1, 2, 3 dans un ordre qui ne suit pas l'ordre des étages (donnée, conteneur, nœud). `SOLUTIONS.md` donne la correspondance.

## B. `5.3-projet/` : squelette et solution de `demo_monitor`

Cahier des charges du plan (texte exact) :
> Un nœud `mission_monitor` dans `demo_ws/src/demo_monitor/` : il s'abonne à l'état de la mission et à `/mavros/battery`, et publie un résumé sur un topic externe (état courant, tension, temps passé dans l'état) à 1 Hz. Il n'arme rien, ne change rien, il regarde. C'est le nœud le plus simple qui oblige à toucher à tout : un paquet, un `package.xml`, une constante dans `topics.py`, un launch, la config.

Règles que le squelette doit illustrer, chacune avec la ligne qui la respecte :
- Le nom du topic vient de `topics.py` : la recrue ajoute `DEMO_SUMMARY = f'{EXTERNAL}/demo/summary'` dans `packages/tools/tools/topics.py` (copie locale du sous-module).
- L'état est comparé à une constante de `MissionState`, pas à une chaîne.
- Pas de `time.sleep` dans un callback : un timer à 1 Hz.
- `package.xml` déclare `rclpy`, `std_msgs`, `sensor_msgs` (`BatteryState` est dans `sensor_msgs` : vérifie), `tools`, `custom_interfaces`.
- Le résumé est externe parce que le sol veut le voir ; le préfixe suffit.
- Logs en français, `INFO` pour les événements (une transition d'état vue, le passage sous `battery_warn_v` en `WARN` une seule fois), jamais de périodique.

Structure :
```
5.3-projet/
  README.md                       une page : le cahier des charges ci-dessus, la liste des fichiers à toucher (paquet, package.xml, topics.py, launch, demo.yaml), ce que make check va relever et pourquoi c'est voulu
  squelette/demo_monitor/         paquet ament_python à copier dans workspaces/demo_ws/src/
    package.xml                   VOLONTAIREMENT incomplet : maintainer `root` `root@todo.todo`, licence `TODO: License declaration`, description `TODO: Package description` ; dépendances présentes
    setup.py, setup.cfg, resource/demo_monitor, demo_monitor/__init__.py
    demo_monitor/monitor.py       squelette : imports, classe, déclaration des paramètres, abonnements et publication en place, corps des callbacks et du timer remplacés par des `# TODO n :` numérotés (5 à 7 TODO), docstring qui renvoie au README
  solution/                       pour les leads
    demo_monitor/                 le paquet complet, métadonnées remplies (Colin Cormier, colinc131@gmail.com, Apache-2.0)
    topics.py.diff                la ligne à ajouter dans topics.py
    mission.launch.py.diff        le nœud ajouté au launch de demo_bringup (même YAML de mission en paramètres)
    CHECKLIST.md                  ce que le lead qui relit la PR vérifie (les six règles ci-dessus)
```

Le paramètre `battery_warn_v` existe déjà dans `demo.yaml` de la tâche 2 : vérifie, et dis-le dans le README (la recrue n'a qu'à le lire, pas à l'ajouter ; si la clé est absente, ajoute un `demo.yaml.diff`).

Le message publié : `std_msgs/String` en JSON compact (`{"state": "GOTO", "voltage": 15.8, "time_in_state": 12.4}`) ; le label d'état vient d'un dict indexé par les constantes de `MissionState`. Isole la mise en forme du résumé dans une fonction de module testable sans ROS.

## Vérification attendue

- `git apply --check` et `git apply -R --check` de chaque patch dans le dépôt de travail du scratchpad (sortie dans le rapport).
- `python -m py_compile` sur tous les `.py` (squelette et solution).
- Exécuter `aeac-2027/scripts/check.py` sur une copie de travail (scratchpad) d'aeac-2027 où `demo_ws` et le squelette sont en place, et montrer qu'il relève exactement les trois métadonnées du squelette ; puis avec la solution à la place, qu'il ne relève rien pour `demo_monitor`. Attention : `check.py` lit `.gitmodules` et `Makefile` relatifs à sa racine ; copie ce qu'il faut ou exécute-le depuis la copie.
- Test hors ROS de la solution avec des stubs dans `sys.modules` (comme la tâche 2) : un état reçu, une tension reçue, le résumé publié contient les trois champs ; passage sous le seuil produit un WARN une seule fois.
- Docker et ROS indisponibles : pas de build ni de launch, dis-le.

## Contraintes globales

- Aucun tiret cadratin (—). Aucun commit, aucun push. Ne modifie ni `aeac-2027` ni `mission-template/` ni `demo_ws/` (si `demo_ws` doit changer pour que le projet marche, décris le changement dans le rapport sans le faire).
- Pas de dossier `test/`.
