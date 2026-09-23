# Tâche 2 : `demo_ws`, la mission démo de la formation 5

Contexte : la formation 5 du club Zenith apprend aux recrues l'environnement de compétition (dépôt de mission `aeac-2027`, dérivé de `mission-template`). Le document 5.2 fait tourner une mission démo en simulation (SITL ArduPilot dans Mission Planner, mavros dans un conteneur). Le template ne contient aucune mission : la démo vit dans le dossier de la formation, et la recrue la copie dans `workspaces/` de son clone, lie les paquets partagés et lance `make sim C=demo`. Proposition P26 du plan d'architecture V3 (texte exact) :

> La formation 5 fournit `demo_ws/` (quatre états `IDLE`, `GOTO`, `ACT`, `RETURN`, un GO externe, un waypoint du YAML, une action factice, retour ; états en constantes de `custom_interfaces`, `_transition()` unique et loggé, paramètre `sim`, topics de `topics.py` ; une centaine de lignes) et guide la recrue : copier `mission-template/`, déposer `demo_ws` dans `workspaces/`, `make link` des partagés, `make sim C=demo`. aeac-2027 ne voit jamais la démo.

Emplacement à créer : `C:\Users\colin\Zenith\Control-Formations\5-env_compétition\demo_ws\` (dépôt git Control-Formations, branche `prep_formation_5_et_aeac2027`).

À lire d'abord, dans `C:\Users\colin\Zenith\aeac-2027` : `ARCHITECTURE.md` (règles de code, tout le fichier), `Makefile` (cibles `sim`, `link`, `build`, `shell`, `bag`), `compose/sim.yml` (comment le launch est appelé : `ros2 launch ${C}_bringup mission.launch.py sim:=true site:=sim`, `ROS_DOMAIN_ID=3`), `config/README.md` (format de `config/<mission>.yaml`), `config/sites/sim.yaml` (format des sites), `packages/sim_mocks/README.md` et `packages/sim_mocks/sim_mocks/rc_simulator.py` (canaux 7, 8, 9 du message `RCIn`, PWM 1100/1500/1900) et `takeoff_test.py`, `workspaces/gcs_ws/src/gcs_bringup/` (exemple de paquet bringup ament_python avec launch), `packages/tools/tools/topics.py` et `packages/custom_interfaces/msg/MissionState.msg` (créés par la tâche 1 : `DEMO_STATE = '/aeac/external/demo/state'` ; constantes `IDLE=0 GOTO=1 ACT=2 RETURN=3`, champs `header`, `state`, `time_in_state`). Pour le style d'un nœud pédagogique : `C:\Users\colin\Zenith\Control-Formations\3-ros2\b3_tools_ws\src\b3_tools\b3_tools\takeoff.py`.

## Contenu à produire

```
demo_ws/
  README.md                         deux paragraphes : ce que fait la démo, comment on l'installe (les 4 commandes)
  src/
    demo_bringup/                   ament_python
      package.xml, setup.py, setup.cfg, resource/demo_bringup, demo_bringup/__init__.py
      launch/mission.launch.py
      config/demo.yaml              à copier par la recrue dans config/ du dépôt
      config/sites/polytechnique.yaml   exemple de second site, à copier dans config/sites/
    demo_mission/                   ament_python
      package.xml, setup.py, setup.cfg, resource/demo_mission, demo_mission/__init__.py
      demo_mission/mission.py       le nœud, environ 100 à 130 lignes
```

Pas de dossier `test/` (règle du dépôt). Métadonnées remplies : maintainer `Colin Cormier` `colinc131@gmail.com`, licence `Apache-2.0`, description en anglais, version `1.0.0`. `package.xml` de `demo_mission` déclare `rclpy`, `std_msgs`, `sensor_msgs`, `mavros_msgs`, `geographic_msgs`, `tools`, `custom_interfaces` (seulement ce qui est réellement importé ; vérifie). `demo_bringup` déclare `demo_mission` en `exec_depend` et `ros2launch`.

## Le launch `mission.launch.py`

Arguments : `sim` (défaut `false`), `site` (défaut `sim`). Il charge deux fichiers YAML depuis le dépôt monté dans `/aeac` : `/aeac/config/demo.yaml` et `/aeac/config/sites/<site>.yaml` (le dépôt est toujours monté à `/aeac` dans les conteneurs, voir `compose/sim.yml`). Un seul nœud : paquet `demo_mission`, exécutable `mission`, nom `demo_mission`, `output='screen'`, paramètres : le YAML de mission, les valeurs du site, et `{'sim': LaunchConfiguration('sim')}`. Le YAML de mission est au format paramètres ROS 2 (`demo_mission: ros__parameters: ...`). Le YAML de site existant (`config/sites/sim.yaml`) n'est PAS au format `ros__parameters` : le launch le lit en Python (module `yaml`) dans une `OpaqueFunction` et aplatit les clés utiles en paramètres (`home.lat`, `home.lon`, `home.alt`, `target.lat`, `target.lon`, `altitude_agl`). Garde le format actuel de `sites/sim.yaml` (clés `site.name`, `site.home.lat|lon|alt`, `site.scene.target.lat|lon`, `site.altitude_agl`) pour ne pas modifier le template. Docstring de haut niveau en français qui explique ce choix en deux phrases.

## `config/demo.yaml` (format `ros__parameters`)

Paramètres : `rc.go_channel: 7` (index dans `RCIn.channels`, canal 8 de la manette, touche `w` du `rc_simulator`), `rc.go_pwm_min: 1700`, `arrival_radius_m: 3.0`, `act_duration_s: 5.0`, `battery_warn_v: 14.0` (inutilisé par la démo, il sert au projet 5.3 ; le dire en commentaire), `state_rate_hz: 2.0`. Un commentaire par paramètre.

## Le nœud `mission.py`

Une machine à états, écrite pour être lue par une recrue :

- États : constantes de `MissionState` (`IDLE`, `GOTO`, `ACT`, `RETURN`), jamais redéfinies. Un dict `LABELS` pour le log est acceptable s'il est indexé par ces constantes.
- Abonnements : `/mavros/state` (`mavros_msgs/State`), `/mavros/rc/in` (`RCIn`), `/mavros/global_position/global` (`sensor_msgs/NavSatFix`, QoS `qos_profile_sensor_data`, sinon rien n'arrive : commente-le). Ces trois noms mavros sont des topics tiers : mets-les dans des constantes de module en tête du fichier avec un commentaire qui dit pourquoi ils ne sont pas dans `topics.py`.
- Publication : `MissionState` sur `topics.DEMO_STATE` à `state_rate_hz`, via un timer ; `header.stamp` rempli, `time_in_state` calculé.
- Setpoints : `geographic_msgs/GeoPoseStamped` sur `/mavros/setpoint_position/global`, publié par le même timer tant qu'on est en `GOTO` ou `RETURN` (mavros exige un flux continu). Altitude : `home.alt + altitude_agl` (une phrase de commentaire sur AMSL vs ellipsoïde, approximation acceptée pour la démo).
- Transitions, toutes par une seule méthode `_transition(self, new_state)` qui met à jour l'état, l'horodatage d'entrée et logue en français en `INFO` (`Transition IDLE -> GOTO`). Règles :
  - `IDLE -> GOTO` : GO reçu (`channels[go_channel] >= go_pwm_min`) ET drone armé ET mode `GUIDED` (sinon un `WARN` une seule fois : « GO reçu mais le drone n'est pas armé en GUIDED »).
  - `GOTO -> ACT` : distance haversine à `target` < `arrival_radius_m`.
  - `ACT -> RETURN` : `act_duration_s` écoulées (vérifié dans le timer). En entrant dans `ACT`, l'action factice : `if not self.sim: self._trigger_payload()` sinon log `Simulation : action factice, rien n'est déclenché`. `_trigger_payload` ne fait qu'un log `WARN` « Déclenchement réel : à implémenter par la mission ». C'est l'unique « appel matériel » de la démo, celui que `sim` entoure : commente-le.
  - `RETURN -> IDLE` : distance à `home` < `arrival_radius_m`. Log `INFO` « Mission terminée ».
- Le nœud n'arme jamais, ne change jamais de mode, n'appelle aucun service. Pas de `time.sleep`. Callbacks courts et un timer.
- Paramètres déclarés avec valeurs par défaut sûres ; `sim` déclaré `False`, lu une fois dans `__init__`.
- Logs : français, `INFO` pour les événements, jamais de log périodique. Code, noms, topics en anglais. Docstring de module en français : ce que fait la démo et les trois questions que la recrue doit pouvoir répondre en la lisant (où sont les noms de topics, où sont les états, où est le waypoint).
- Isole la logique pure dans des fonctions de module testables sans ROS : `haversine_m(lat1, lon1, lat2, lon2)` et `next_state(state, *, go, armed, guided, dist_target_m, dist_home_m, elapsed_s, params)` qui renvoie le nouvel état ou `None`. Le nœud les appelle.

## `sites/polytechnique.yaml`

Mêmes clés que `sim.yaml`. Home : lat 45.5048, lon -73.6132, alt 60.0 ; target : lat 45.5056, lon -73.6120 ; altitude_agl 10.0 ; commentaire : coordonnées approximatives du campus, à remplacer par le terrain réel.

## README.md de `demo_ws`

Paragraphe 1 : ce que fait la démo (quatre états, GO par la manette, waypoint du site, action factice, retour). Paragraphe 2 : installation en quatre commandes depuis la racine du clone : `cp -r <dossier de la formation>/demo_ws workspaces/`, `cp workspaces/demo_ws/src/demo_bringup/config/demo.yaml config/`, `make link C=demo PKG=tools && make link C=demo PKG=custom_interfaces`, `make build C=demo`. Puis `make sim C=demo`. Cinq lignes maximum pour les topics et paramètres (règle P31 : README de cinq lignes par paquet).

## Vérification attendue

- `python -m py_compile` sur chaque `.py` ; `python -c "import yaml; yaml.safe_load(open(...))"` sur les YAML (installe PyYAML dans un venv du scratchpad si absent).
- Test hors ROS de `haversine_m` et `next_state` : un script dans le scratchpad (pas dans le dépôt) qui importe `mission.py` avec des stubs minimaux pour `rclpy`, `mavros_msgs`, `sensor_msgs`, `geographic_msgs`, `std_msgs`, `tools`, `custom_interfaces` insérés dans `sys.modules`, et vérifie la séquence IDLE -> GOTO -> ACT -> RETURN -> IDLE, le refus du GO sans GUIDED, et la distance Canberra home/target (environ 65 m). Rapporte la commande et la sortie.
- Docker et ROS ne sont pas disponibles : aucun `colcon build` ni `ros2 launch`. Dis-le.
- `wc -l` du nœud et du launch.

## Contraintes globales

- Aucun tiret cadratin (—) nulle part. Aucun `git commit` : le contrôleur commet ; ne fais que créer les fichiers. Aucun push.
- Ne modifie rien dans `aeac-2027` ni dans `mission-template/` (si un fichier de là doit changer, dis-le dans le rapport).
- Pas de dossier `test/`, pas de pytest dans le dépôt.
