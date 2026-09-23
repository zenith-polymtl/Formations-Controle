# CHECKLIST.md : relecture de la PR `mission_monitor`

Pour le lead. Six règles, six questions, dans l'ordre où elles se lisent dans le diff. Une
réponse manquante ne bloque pas la PR toute seule ; c'est la conversation qui compte, la PR
est le prétexte.

## 1. Le nom du topic vient de `topics.py`

- [ ] `packages/tools/tools/topics.py` gagne `DEMO_SUMMARY = f'{EXTERNAL}/demo/summary'`, dans
      la section des externes. En formation, cette ligne reste une modification locale du
      sous-module : elle n'est pas commise, elle est citée dans la description de la PR, et
      c'est le lead qui la porte ensuite dans le dépôt `tools`.
- [ ] Le nœud publie sur `topics.DEMO_SUMMARY`. Aucun `'/aeac/...'` écrit en clair nulle part,
      ni dans le nœud, ni dans le launch.
- [ ] `/mavros/battery` est une constante de module du nœud et n'est pas dans `topics.py` :
      `topics.py` ne décrit que les topics `/aeac` écrits par l'équipe.

Question à poser : « si on renomme le topic demain, combien de fichiers changent ? »

## 2. L'état se compare à une constante de `MissionState`

- [ ] Aucune comparaison à une chaîne (`== 'IDLE'`) ni à un entier nu (`== 0`).
- [ ] Le dict des labels est indexé par `MissionState.IDLE`, `.GOTO`, `.ACT`, `.RETURN`, et
      c'est le seul endroit où les noms d'états apparaissent en texte.
- [ ] Le cas « aucun état reçu » est traité (`None`, label `INCONNU`), pas confondu avec `IDLE`.

Question à poser : « que publie ton nœud dans la seconde qui suit son démarrage, avant que la
mission ait parlé ? »

## 3. Pas de `time.sleep` dans un callback

- [ ] La publication est dans le callback d'un `create_timer` à 1 Hz, pas dans un `while` ni
      après un `sleep`.
- [ ] Les deux callbacks d'abonnement ne font que retenir des valeurs : pas de publication,
      pas d'attente, pas de calcul long.

Question à poser : « où part le callback de la batterie pendant que le tien dort ? »

## 4. `package.xml` déclare ce qui est importé

- [ ] `rclpy`, `std_msgs`, `sensor_msgs`, `tools`, `custom_interfaces` : un `<depend>` par
      import du fichier, ni plus ni moins.
- [ ] `sensor_msgs` et non `mavros_msgs` pour `BatteryState` : demander comment la recrue l'a
      vérifié (`ros2 interface show sensor_msgs/msg/BatteryState`).
- [ ] Mainteneur réel avec un courriel réel, licence `Apache-2.0`, description en une phrase
      qui dit ce que le paquet fait. `make check` ne doit plus rien dire sur `demo_monitor`.
- [ ] `setup.py` porte les mêmes quatre champs, et `entry_points` déclare
      `monitor = demo_monitor.monitor:main`. `check.py` ne regarde pas `setup.py` : c'est au
      lead de le faire.
- [ ] Pas de dossier `test/` généré par `ros2 pkg create`.

## 5. Le résumé est externe, et le préfixe suffit

- [ ] Le topic est sous `EXTERNAL`, pas sous `INTERNAL`, et la recrue sait dire pourquoi : le
      sol veut voir le résumé, donc il traverse la radio.
- [ ] Aucune configuration Zenoh n'a été touchée : le préfixe est toute la décision.
- [ ] Le débit reste raisonnable : 1 Hz de JSON court sur la radio, pas un `MissionState`
      complet à 10 Hz.

## 6. Logs en français, événements seulement

- [ ] Un `INFO` au démarrage, un `INFO` par transition d'état.
- [ ] Un `WARN` au passage sous `battery_warn_v`, une seule fois, avec la tension et le seuil
      dans le message ; et le mécanisme qui le réarme est visible et expliqué.
- [ ] Le réarmement demande une petite marge au-dessus du seuil (`battery_warn_v + 0.3`) et
      non le seuil nu : sinon une tension qui oscille sur le seuil ressort une ligne par
      message, et c'est exactement ce que fait une batterie sous charge.
- [ ] Rien dans `tick()` : aucun log à chaque tour de timer.
- [ ] Les messages sont en français, le code et les noms de topics en anglais.

Question à poser : « si la tension oscille de quelques centièmes de volt autour du seuil,
combien de lignes sortent ? » La bonne réponse est une, et elle demande la marge ci-dessus.

## Le reste de la PR

- [ ] `config/demo.yaml` gagne une section `mission_monitor: ros__parameters:` avec
      `battery_warn_v`. Le seuil n'est réécrit ni dans le launch, ni dans le nœud autrement
      que comme défaut de déclaration. Un fichier de paramètres ROS 2 est indexé par nom de
      nœud : voir `5.3-projet/README.md`, « Les fichiers à toucher ».
- [ ] Le launch lance le moniteur en même temps que la mission et lui passe
      `config/demo.yaml` tel quel, sans relire le YAML lui-même. Si la recrue a ajouté ses clés
      sous `demo_mission:` au lieu d'une section à son nom, le nœud tourne quand même et rien
      n'échoue : lui faire lancer `ros2 param get /mission_monitor battery_warn_v` et constater
      que le seuil est resté au défaut du code. C'est la panne la plus discrète du projet, et
      la raison d'être du cinquième fichier à toucher.
- [ ] La mise en forme du résumé est dans une fonction de module, sans appel ROS, et la recrue
      l'a essayée dans un `python3` nu.
- [ ] `voltage` absent vaut `null` et non `0.0`, et la recrue sait dire pourquoi ça compte
      pour celui qui lit au sol.
- [ ] Une tension `NaN` est traitée comme une tension absente, dans le callback comme dans la
      mise en forme : `sensor_msgs/BatteryState` met `NaN` dans les champs non mesurés, un
      `NaN` comparé au seuil ne déclenche rien et `json.dumps` en ferait un `NaN` qui n'est pas
      du JSON. La garde est voulue aux deux endroits : c'est une redondance assumée, l'un
      protège le journal, l'autre protège le JSON envoyé au sol.
- [ ] Le temps dans l'état est celui que la mission publie, republié tel quel : le moniteur ne
      tient pas de chronomètre à lui.
- [ ] La recrue sait que ce résumé ne prouve pas que le nœud de mission est vivant : il sort à
      1 Hz même si la mission est morte, avec le dernier état reçu. Un résumé qui arrive n'est
      pas une mission qui va bien.
- [ ] Le nœud ne publie rien vers mavros, n'appelle aucun service, ne change aucun mode. Il
      regarde.
