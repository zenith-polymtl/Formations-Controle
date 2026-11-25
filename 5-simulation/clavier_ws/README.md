# clavier_ws : piloter le drone au clavier dans l'environnement de compétition

La téléop et la node de contrôle clavier de la formation 3.4, plus un
launch file `clavier_bringup/launch/mission.launch.py` au nom que `make sim` attend. Les deux
nodes ne démarrent qu'avec `sim:=true` : sur le drone, ce launch file ne lance rien.
Un seul changement par rapport à la solution 3.4 : sans touche, `keyboard_control` n'envoie
rien, pour laisser décoller en GUIDED (expliqué en tête du fichier).
`src/sim_mocks` est un lien vers `packages/sim_mocks` du template : il donne `make takeoff`.

Depuis la racine d'un clone de `mission-template` :

```bash
cp -r <dossier de la formation>/5-simulation/clavier_ws workspaces/
make build C=clavier
```

Puis :

1. `make sim C=clavier`, et ce terminal garde le focus.
2. Décoller : Mission Planner (GUIDED, Arm, clic droit sur la carte, Takeoff, 10 m), ou `make takeoff` dans un deuxième terminal. Puis, dans le premier terminal : `w a s d` pour se déplacer, `r f` pour monter et descendre, `q e` pour tourner. Relâcher : le drone s'arrête.
3. Mode RTL dans Mission Planner, puis `Ctrl-C` et `make down`.
