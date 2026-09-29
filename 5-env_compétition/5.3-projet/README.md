# Projet du document 5.3 : la node `mission_monitor`

Ce dossier contient l'énoncé du projet. Le mode d'emploi, pas à pas, est dans le document [5.3](../5.3-projet-ajouter-un-node.md).

## Le cahier des charges

Vous écrivez une node `mission_monitor`, dans un package `demo_monitor` placé dans `workspaces/demo_ws/src/`. Elle écoute l'état de la mission et `/mavros/battery` (deux subscribers), et publie à 1 Hz un résumé sur un topic externe : l'état courant, la tension, le temps passé dans l'état. Elle n'arme rien et ne commande rien : elle ne fait qu'observer.

Le résumé est un `std_msgs/String` qui contient du JSON sur une ligne :

```json
{"state": "GOTO", "voltage": 15.8, "time_in_state": 12.4}
```

`voltage` vaut `null` tant qu'aucune mesure n'est arrivée : une batterie qu'on n'a pas mesurée n'est pas une batterie à zéro volt. `time_in_state` n'est pas calculé par le moniteur : la mission le publie, et le moniteur le republie.

Quand la tension passe sous `battery_warn_v` (14.0 V, réglé dans `config/demo.yaml`), la node écrit un `WARN`, une seule fois par lancement.

Le résumé dit ce que le moniteur a vu. Il ne dit pas que la mission va bien : il sort à 1 Hz même si la node de mission est morte. Pour savoir si la mission est vivante, utilisez `ros2 node list`.

## Les fichiers à toucher, dans l'ordre

| Fichier | Ce qu'on y fait | Section de 5.3 |
|---|---|---|
| `workspaces/demo_ws/src/demo_monitor/` | Copier le squelette | 2.1 |
| `workspaces/demo_ws/src/demo_monitor/demo_monitor/monitor.py` | Les six TODO | 2.2 et 2.3 |
| `packages/tools/tools/topics.py` | Ajouter `DEMO_SUMMARY = f'{EXTERNAL}/demo/summary'`. `tools` est un submodule, donc un autre repo : la ligne reste une modification locale, hors de votre commit, et le lead la porte dans `tools` | 2.4 |
| `workspaces/demo_ws/src/demo_bringup/launch/mission.launch.py` | Ajouter la node au launch file | 3.1 |
| `workspaces/demo_ws/src/demo_bringup/package.xml` | Ajouter `<exec_depend>demo_monitor</exec_depend>` : le launch file lance le moniteur, donc `demo_bringup` en dépend | 3.1 |
| `config/demo.yaml`, à la racine du clone | Ajouter une section `mission_monitor:` avec `battery_warn_v: 14.0` | 3.2 |
| `workspaces/demo_ws/src/demo_monitor/package.xml` et `setup.py` | Remplir les champs mainteneur, courriel, licence (`Apache-2.0`) et description, que le squelette laisse vides exprès | 3.5 |

## Les six règles

La section 2.3 du document 5.3 détaille chaque règle, avec la ligne du fichier qui la respecte. Voici seulement la liste :

1. Le nom du topic vient de `topics.py`.
2. L'état se compare à une constante de `MissionState`.
3. Pas de `time.sleep` dans un callback.
4. `package.xml` déclare ce qui est importé.
5. Le résumé est externe parce que le sol veut le voir.
6. Logs en français, `INFO` pour les événements, jamais de log périodique.

## C'est fini quand

1. Avec `make sim C=demo` qui tourne, `ros2 topic hz /aeac/external/demo/summary` donne environ 1 Hz, et le champ `state` du résumé passe de `IDLE` à `GOTO` au GO.
2. `ros2 param get /mission_monitor battery_warn_v` suit la valeur de `config/demo.yaml` : vous avez essayé la valeur `11.0`, puis remis `14.0`.
3. `make check`, dans WSL hors conteneur, répond `check : rien à signaler`.
4. Une PR est ouverte sur `mission-template` depuis votre branche `prenom/demo`, avec la ligne de `topics.py` dans sa description.

Le lead relit la PR avec [`solution/CHECKLIST.md`](solution/CHECKLIST.md). La grille est publique, et c'est une bonne idée de la lire avant de déposer votre PR.

## Dossiers

- `squelette/demo_monitor/` : le package à copier dans `workspaces/demo_ws/src/`.
- `solution/` : le package complet, les quatre diffs (`topics.py`, le launch file, le `package.xml` de `demo_bringup`, `demo.yaml`) et `CHECKLIST.md`. Ouvrez ce dossier seulement après avoir vraiment essayé.
