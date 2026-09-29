# CHECKLIST.md : relecture de la PR `mission_monitor`

Pour le lead. Six règles, dans l'ordre où elles se lisent dans le diff, puis le reste de la PR.
La PR sera fermée sans merge de toute façon (5.3, section 4) : une case vide est un sujet de
conversation, pas un refus.

## 1. Le nom du topic vient de `topics.py`

- [ ] `packages/tools/tools/topics.py` gagne `DEMO_SUMMARY = f'{EXTERNAL}/demo/summary'`, dans
      la section des externes. En formation, cette ligne reste une modification locale du
      submodule : elle n'entre pas dans le commit, elle est citée dans la description de la PR, et
      c'est le lead qui la porte ensuite dans le repo `tools`.
- [ ] La node publie sur `topics.DEMO_SUMMARY`. Aucun nom de topic `'/aeac/...'` écrit en
      clair, ni dans la node, ni dans le launch file (le `CONFIG_DIR = '/aeac/config'` du
      launch file est un dossier du conteneur, pas un topic : il reste).
- [ ] `/mavros/battery` est une constante en tête de la node, l'exception que prévoit
      `ARCHITECTURE.md` pour les topics de mavros, et n'est pas dans `topics.py` : `topics.py`
      ne décrit que les topics `/aeac` écrits par l'équipe.

Question à poser : « si on renomme le topic demain, combien de fichiers changent ? »

## 2. L'état se compare à une constante de `MissionState`

- [ ] Aucune comparaison à une chaîne (`== 'IDLE'`) ni à un entier nu (`== 0`).
- [ ] Le dict des labels est indexé par `MissionState.IDLE`, `.GOTO`, `.ACT`, `.RETURN`, et
      c'est le seul endroit où les noms d'états apparaissent en texte.
- [ ] Le cas « aucun état reçu » est traité (`None`, label `INCONNU`), pas confondu avec `IDLE`.

Question à poser : « que publie ta node dans la seconde qui suit son démarrage, avant que la
mission ait parlé ? »

## 3. Pas de `time.sleep` dans un callback

- [ ] La publication est dans le callback d'un `create_timer` à 1 Hz, pas dans un `while` ni
      après un `sleep`.
- [ ] Les deux callbacks des subscribers ne font que retenir des valeurs : pas de publication,
      pas d'attente, pas de calcul long.

Question à poser : « où part le callback de la batterie pendant que le tien dort ? »

## 4. `package.xml` déclare ce qui est importé

- [ ] `rclpy`, `std_msgs`, `sensor_msgs`, `tools`, `custom_interfaces` : un `<depend>` par
      import du fichier, ni plus ni moins.
- [ ] `sensor_msgs` et non `mavros_msgs` pour `BatteryState` : demander comment la recrue l'a
      vérifié (`ros2 interface show sensor_msgs/msg/BatteryState`).
- [ ] Mainteneur réel avec un courriel réel, licence `Apache-2.0`, description en une phrase
      qui dit ce que le package fait. `make check` ne doit plus rien dire sur `demo_monitor`.
- [ ] `setup.py` porte les mêmes quatre champs, et `entry_points` déclare
      `monitor = demo_monitor.monitor:main`. `check.py` ne regarde pas `setup.py` : c'est au
      lead de le faire.
- [ ] Le `package.xml` de `demo_bringup` gagne `<exec_depend>demo_monitor</exec_depend>` : son
      launch file lance le moniteur, donc il en dépend (voir `package.xml.diff`).

## 5. Le résumé est externe, et le préfixe suffit

- [ ] Le topic est sous `EXTERNAL`, pas sous `INTERNAL`, et la recrue sait dire pourquoi : le
      sol veut voir le résumé, donc il traverse la radio.
- [ ] Aucune configuration Zenoh n'a été touchée : le préfixe est toute la décision.
- [ ] Le débit reste raisonnable : 1 Hz de JSON court sur la radio, pas un `MissionState`
      complet à 10 Hz.

## 6. Logs en français, événements seulement

- [ ] Un `INFO` au démarrage, un `INFO` par transition d'état.
- [ ] Un `WARN` au passage sous `battery_warn_v`, une seule fois par lancement, avec la tension
      et le seuil dans le message.
- [ ] Rien dans `tick()` : aucun log à chaque tour de timer.
- [ ] La recrue sait pourquoi le `WARN` sort dès le démarrage en SITL : le SITL simule une
      batterie d'environ 12.6 V, sous le seuil de 14.0 V réglé pour la batterie du drone. Le
      test de 5.3, section 3.4 (seuil à `11.0`, le `WARN` disparaît), montre que le seuil vient
      bien du YAML.
- [ ] Les messages sont en français, le code et les noms de topics en anglais.

Question à poser : « si la tension oscille de quelques centièmes de volt autour du seuil,
combien de lignes sortent ? » La bonne réponse est une, grâce à `battery_warned`.

## Le reste de la PR

- [ ] `config/demo.yaml` gagne une section `mission_monitor: ros__parameters:` avec
      `battery_warn_v`. Le seuil n'est réécrit ni dans le launch file, ni dans la node autrement
      que comme défaut de déclaration. Un fichier de paramètres ROS 2 est indexé par nom de
      node : voir 5.3, section 3.2.
- [ ] Le launch file lance le moniteur en même temps que la mission et lui passe
      `config/demo.yaml` tel quel, sans relire le YAML lui-même. Si la recrue a ajouté ses clés
      sous `demo_mission:` au lieu d'une section à son nom, la node tourne quand même et rien
      n'échoue : lui faire lancer `ros2 param get /mission_monitor battery_warn_v` et constater
      que le seuil est resté au défaut du code. C'est la panne la plus discrète du projet, et
      la raison d'être du cinquième fichier à toucher.
- [ ] La mise en forme du résumé est dans une fonction de module, sans appel ROS, et la recrue
      l'a essayée seule dans `python3`, dans `make shell` (5.3, section 3.4).
- [ ] `voltage` absent vaut `null` et non `0.0`, et la recrue sait dire pourquoi ça compte
      pour celui qui lit au sol.
- [ ] Le temps dans l'état est celui que la mission publie, republié tel quel : le moniteur ne
      tient pas de chronomètre à lui.
- [ ] La recrue sait que ce résumé ne prouve pas que la node de mission est vivante : il sort à
      1 Hz même si la mission est morte, avec le dernier état reçu. Un résumé qui arrive n'est
      pas une mission qui va bien.
- [ ] La node ne publie rien vers mavros, n'appelle aucun service, ne change aucun mode. Elle
      regarde.
