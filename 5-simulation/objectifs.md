# Formation 5 : simulation avancée

Documents : [5.1](5.1-simulation-sitl-ardupilot.md), [5.2](5.2-gazebo.md).

Prérequis : formation 1 (le SITL dans Mission Planner), formation 3.4 (piloter au clavier), formation 4.1 (le clone de `mission-template`).

Voici les objectifs de chaque document :

- **la formation 5.1, simulation SITL ArduPilot** : copier `clavier_ws` (les nodes de la 3.4 et un launch file) dans `mission-template/workspaces/`, `make build C=clavier`, `make sim C=clavier`, `make echo T=/mavros/state`, décoller avec Mission Planner ou `make takeoff`, voler au clavier, revenir en RTL ; en bonus, démarrer le SITL à Medicine Hat. C'est réussi si mavros affiche `connected: true`, si le drone suit `w a s d` et `r f`, et s'il revient se poser en RTL.
- **la formation 5.2, Gazebo avec Keen-Kestrel** : cloner Keen-Kestrel, `make gazebo`, se connecter avec une GCS (Mission Planner en UDP 14550 ou `make mavproxy`), changer de scène (`make t1`, `make t2`), puis brancher le même `clavier_ws` avec `make sim C=clavier SITL=gazebo`. C'est réussi si l'Hexa décolle et se pose depuis une GCS, si `make t2` fait apparaître l'ODOS, et si l'Hexa suit le clavier dans Gazebo.
