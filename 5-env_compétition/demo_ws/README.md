# demo_ws : la mission démo de la formation 5

La démo est une mission de compétition réduite à son squelette : une machine à quatre états
(`IDLE`, `GOTO`, `ACT`, `RETURN`). Le node attend un GO sur un interrupteur de la manette,
vérifie que le pilote a armé en GUIDED, vole vers le waypoint du site en publiant un setpoint
global, y attend quelques secondes en déclenchant l'action de la mission, puis revient au point
de départ et repasse en `IDLE`. Il n'arme jamais, ne change jamais de mode et n'appelle aucun
service : c'est le pilote qui pilote, le code se contente de suivre.

Installation dans un clone de `mission-template`, depuis la racine du clone : trois gestes.

```bash
cp -r <dossier de la formation>/5-env_compétition/demo_ws workspaces/
cp workspaces/demo_ws/src/demo_bringup/config/demo.yaml config/
make build C=demo
```

`src/tools`, `src/custom_interfaces` et `src/sim_mocks` sont des liens vers `packages/` livrés
avec le workspace : il n'y a pas de `make link` à faire. Copiés depuis Windows, ils arrivent en
fichiers texte qui contiennent le chemin visé : `make build` les recrée en liens.

Ensuite, avec le SITL lancé dans Mission Planner :

```bash
make sim C=demo                           # terminal 1 : mavros et la mission, Ctrl-C arrête le launch
make takeoff                              # terminal 2 : arme et décolle
make rc                                   # terminal 2 : la touche w envoie le GO
make echo T=/aeac/external/demo/state     # terminal 3
make down                                 # en fin de séance
```

Le terrain se choisit avec `SITE=<nom>` (`sim` par défaut), parmi les fichiers de
`config/sites/` du repo : `make sim C=demo SITE=cimetiere`. Les logs de mavros :
`make logs IMG=mavros-sim`.

Publie `MissionState` sur `topics.DEMO_STATE` et `GeoPoseStamped` sur
`/mavros/setpoint_position/global` ; écoute `/mavros/state`, `/mavros/rc/in` et
`/mavros/global_position/global`. Paramètres : `config/demo.yaml` (`rc.go_channel`,
`rc.go_pwm_min`, `arrival_radius_m`, `act_duration_s`, `state_rate_hz`),
`config/sites/<site>.yaml` (`home`, `target`, `altitude_agl`) et `sim`, donné par le launch file.
