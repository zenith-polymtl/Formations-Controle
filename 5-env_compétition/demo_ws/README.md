# demo_ws : la mission démo de la formation 5

La démo est une mission de compétition réduite à son squelette : une machine à quatre états
(`IDLE`, `GOTO`, `ACT`, `RETURN`). Le nœud attend un GO sur un interrupteur de la manette,
vérifie que le pilote a armé en GUIDED, vole vers le waypoint du site en publiant un setpoint
global en continu, y attend quelques secondes en déclenchant une action factice, puis revient au
point de départ et repasse en `IDLE`. Il n'arme jamais, ne change jamais de mode et n'appelle
aucun service : c'est le pilote qui pilote, le code se contente de suivre.

Installation dans un clone de `mission-template`, depuis la racine du clone, puis `make sim
C=demo` (SITL lancé dans Mission Planner) et, dans un second terminal, `make shell C=demo IMG=sim` puis
`ros2 run sim_mocks rc_simulator` : la touche `w` envoie le GO. Le second site d'exemple se copie
dans `config/sites/` de la même façon que `demo.yaml` et se choisit avec `site:=polytechnique`.

```bash
cp -r <dossier de la formation>/5-env_compétition/demo_ws workspaces/
cp workspaces/demo_ws/src/demo_bringup/config/demo.yaml config/
cp workspaces/demo_ws/src/demo_bringup/config/sites/polytechnique.yaml config/sites/
make link C=demo PKG=tools && make link C=demo PKG=custom_interfaces && make link C=demo PKG=sim_mocks
make build C=demo && make sim C=demo
```

Publie `MissionState` sur `topics.DEMO_STATE` et `GeoPoseStamped` sur
`/mavros/setpoint_position/global` ; écoute `/mavros/state`, `/mavros/rc/in` et
`/mavros/global_position/global`. Paramètres : `config/demo.yaml` (`rc.go_channel`,
`rc.go_pwm_min`, `arrival_radius_m`, `act_duration_s`, `state_rate_hz`),
`config/sites/<site>.yaml` (`home`, `scene.target`, `altitude_agl`) et `sim`, donné par le launch.
