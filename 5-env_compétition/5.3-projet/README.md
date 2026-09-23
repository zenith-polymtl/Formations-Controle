# Projet du document 5.3 : le nœud `mission_monitor`

## Le cahier des charges

> Un nœud `mission_monitor` dans `demo_ws/src/demo_monitor/` : il s'abonne à l'état de la
> mission et à `/mavros/battery`, et publie un résumé sur un topic externe (état courant,
> tension, temps passé dans l'état) à 1 Hz. Il n'arme rien, ne change rien, il regarde. C'est
> le nœud le plus simple qui oblige à toucher à tout : un paquet, un `package.xml`, une
> constante dans `topics.py`, un launch, la config.

Le message publié est un `std_msgs/String` contenant du JSON sur une ligne :

```json
{"state": "GOTO", "voltage": 15.8, "time_in_state": 12.4}
```

`voltage` vaut `null` tant qu'aucune mesure n'est arrivée, et aussi quand la mesure arrive vide
(`sensor_msgs/BatteryState` met `NaN` dans les champs que l'autopilote ne renseigne pas, et
`NaN` n'est pas du JSON) : une batterie qu'on n'a pas mesurée n'est pas une batterie à zéro
volt. `time_in_state` n'est pas calculé par le moniteur : la mission le publie, il le republie.

Ce résumé dit ce que le moniteur a vu, pas que la mission va bien : il sort à 1 Hz même si le
nœud de mission est mort. Il ne prouve donc pas qu'il est vivant, `ros2 node list` le dit.

## Par où commencer

Copier le squelette dans le workspace de la démo, dans le clone du dépôt de mission :

```bash
cp -r <dossier de la formation>/5-env_compétition/5.3-projet/squelette/demo_monitor workspaces/demo_ws/src/
make build C=demo
```

`make build C=demo` réussit : le paquet compile tel quel, les imports, la classe, le
paramètre, les abonnements, la publication et le timer sont en place. Il reste six
`# TODO n :`, tous dans `demo_monitor/monitor.py`, et tant qu'ils ne sont pas écrits le nœud ne
publie rien. Le voir tourner demande le launch et la ligne de `topics.py` : c'est la section 3
du document 5.3.

## Les fichiers à toucher

| Fichier | Ce qu'on y fait |
|---|---|
| `workspaces/demo_ws/src/demo_monitor/demo_monitor/monitor.py` | Les six TODO |
| `workspaces/demo_ws/src/demo_monitor/package.xml` | Remplir mainteneur, licence, description |
| `workspaces/demo_ws/src/demo_monitor/setup.py` | Les mêmes trois champs, et vérifier l'entrée `monitor` |
| `packages/tools/tools/topics.py` | Ajouter `DEMO_SUMMARY` (sous-module : pour la formation, on s'arrête à la modification locale, voir 5.3, section 2.4) |
| `workspaces/demo_ws/src/demo_bringup/launch/mission.launch.py` | Ajouter le nœud au launch |
| `config/demo.yaml` | Ajouter la section `mission_monitor:` avec `battery_warn_v: 14.0` |

Sur la dernière ligne du tableau : un fichier de paramètres ROS 2 est indexé par nom de nœud,
c'est-à-dire que le premier niveau du YAML est le nom du nœud qui recevra les clés qui suivent.
`config/demo.yaml` commence par `demo_mission:`, donc le passer tel quel à un nœud nommé
`mission_monitor` ne lui donne rien, sans erreur ni avertissement : les paramètres restent aux
défauts écrits dans le code. Le moniteur a donc sa propre section dans le même fichier, que le
launch passe aux deux nœuds ; le seuil ne s'écrit nulle part ailleurs dans le nœud.

Le fichier à modifier est celui de la racine du clone, que le launch lit. Une fois la section
`mission_monitor:` ajoutée, ne recopiez plus par-dessus le `demo.yaml` du workspace
(`demo_ws/src/demo_bringup/config/`) : c'est la version d'origine, il effacerait votre section.

`topics.py` est dans `packages/tools`, qui est un sous-module : c'est un autre dépôt, avec sa
propre PR. On ajoute la ligne là-bas, on la fait relire, puis on avance le pointeur du dépôt de
mission (`make bump PKG=tools`). C'est lent exprès : un nom de topic est une frontière. Pour la
formation, on s'arrête à la modification locale : voir 5.3, section 2.4.

## Les six règles

1. **Le nom du topic vient de `topics.py`**, jamais d'une chaîne écrite dans le nœud.
2. **L'état se compare à une constante de `MissionState`**, jamais à `'IDLE'` ni à `0`.
3. **Pas de `time.sleep` dans un callback** : la publication périodique appartient à un timer.
4. **`package.xml` déclare ce qui est importé** : `rclpy`, `std_msgs`, `sensor_msgs`, `tools`, `custom_interfaces`.
5. **Le résumé est externe parce que le sol veut le voir**, et le préfixe `EXTERNAL` suffit.
6. **Logs en français, `INFO` pour les événements, jamais de périodique** ; le `WARN` batterie une seule fois.

Chacune est reprise, avec la ligne du fichier qui la respecte, dans la section 2.3 du document
[5.3](../5.3-projet-ajouter-un-noeud.md), et relue avec
[`solution/CHECKLIST.md`](solution/CHECKLIST.md), publique : la lire avant de déposer sa PR est
une bonne idée.

## Ce que `make check` va relever, et pourquoi c'est voulu

Le squelette est livré avec les trois champs que `ros2 pkg create` laisse en place :

```
workspaces/demo_ws/src/demo_monitor/package.xml: mainteneur à remplir
workspaces/demo_ws/src/demo_monitor/package.xml: licence à remplir (Apache-2.0)
workspaces/demo_ws/src/demo_monitor/package.xml: description à remplir
```

Ces trois lignes sont l'exercice : `make check` doit sortir en erreur sur le squelette et ne
plus rien dire sur `demo_monitor` quand le projet est fini. Un `package.xml` dont le mainteneur
est `root@todo.todo` dit à celui qui trouve le bug six mois plus tard qu'il n'y a personne à qui
demander, et une licence vide interdit de publier le dépôt. Le même travail est à faire dans
`setup.py`, que `check.py` ne regarde pas.

## Vérifier son travail

```bash
make build C=demo && make sim C=demo
# dans un second terminal
make shell C=demo IMG=sim
ros2 topic list | grep summary          # /aeac/external/demo/summary
ros2 topic hz /aeac/external/demo/summary   # environ 1 Hz
ros2 topic echo --once /aeac/external/demo/summary
ros2 param get /mission_monitor battery_warn_v   # 14.0, venu de config/demo.yaml
make check                              # plus rien sur demo_monitor
```

Le `14.0` ne prouve rien tout seul, puisque c'est aussi le défaut du code : pour savoir si la
section est bien lue, mettre `13.1` dans le YAML, relancer, et regarder si le nœud suit.

## Dossiers

- `squelette/demo_monitor/` : le paquet à copier dans `workspaces/demo_ws/src/`.
- `solution/` : pour les leads. Le paquet complet, les trois diffs (`topics.py`, le launch,
  `demo.yaml`) et `CHECKLIST.md`. À ne pas distribuer avant la fin de l'atelier.
