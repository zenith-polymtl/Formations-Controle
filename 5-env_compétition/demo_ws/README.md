# demo_ws : la mission démo de la formation 5

La démo est une mission de compétition réduite à l'essentiel : une machine à quatre états
(`IDLE`, `GOTO`, `ACT`, `RETURN`). D'abord, la node attend un GO sur un interrupteur de la
manette et vérifie que le pilote a armé en GUIDED. Ensuite, elle vole vers le waypoint du site
en publiant un setpoint global. Elle y reste quelques secondes, pendant lesquelles elle
déclenche l'action de la mission. Enfin, elle revient au point de départ et repasse en `IDLE`.
La node n'arme jamais et ne change jamais de mode : ces décisions reviennent au pilote, et le
code se contente de suivre. La node appelle un seul service, `/mavros/set_message_interval`,
pour demander la position du drone à l'autopilote.

Pour installer la démo dans un clone de `mission-template`, tapez ces trois commandes depuis la
racine du clone. Remplacez `<dossier de la formation>` par le chemin de votre clone de
Formations-Controle : `~/Formations-Controle` si vous avez suivi la formation 2.

```bash
cp -r <dossier de la formation>/5-env_compétition/demo_ws workspaces/
cp workspaces/demo_ws/src/demo_bringup/config/demo.yaml config/
make build C=demo
```

`src/tools`, `src/custom_interfaces` et `src/sim_mocks` sont des liens vers `packages/`, livrés
avec le workspace. Vous n'avez donc pas de `make link` à faire. Si vous copiez le workspace
depuis Windows, ces liens arrivent sous forme de fichiers texte qui contiennent le chemin visé.
`make build` les recrée alors en liens.

Ensuite, avec le SITL lancé dans Mission Planner :

```bash
make sim C=demo                           # terminal 1 : mavros et la mission, Ctrl-C arrête le launch
make takeoff                              # terminal 2 : arme et décolle
make rc                                   # terminal 2 : la touche w envoie le GO
make echo T=/aeac/external/demo/state     # terminal 3
make down                                 # en fin de séance
```

Choisissez le terrain avec `SITE=<nom>` (`sim` par défaut), parmi les fichiers de
`config/sites/` du repo. Par exemple : `make sim C=demo SITE=cimetiere`. Pour voir les logs de
mavros, lancez `make logs IMG=mavros-sim`.

La node publie `MissionState` sur `topics.DEMO_STATE` et `GlobalPositionTarget` sur
`/mavros/setpoint_raw/global`. Elle écoute `/mavros/state`, `/mavros/rc/in`,
`/mavros/home_position/home` et `/mavros/global_position/global`. Elle appelle
`/mavros/set_message_interval`. Ses paramètres viennent de `config/demo.yaml` (`rc.go_channel`,
`rc.go_pwm_min`, `arrival_radius_m`, `act_duration_s`, `state_rate_hz`), de
`config/sites/<site>.yaml` (`target`, en mètres depuis le home de l'autopilote, et
`altitude_agl`) et de `sim`, un paramètre donné par le launch file.
