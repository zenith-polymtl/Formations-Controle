# Dépôt de mission

Le code qui vole sur les drones de Zenith : nœuds ROS 2, conteneurs, configuration, déploiement. Une mission = un workspace dans `workspaces/`. Lire [ARCHITECTURE.md](ARCHITECTURE.md) (une page) avant de toucher à quoi que ce soit.

## Démarrage rapide (poste WSL, formation 2 faite)

```bash
git clone --recurse-submodules <url du dépôt>
cd <dépôt>
make init                 # sous-modules, réglages git, dossiers ignorés
make build C=gcs          # construit le workspace gcs_ws dans le conteneur de développement
make dev                  # entre dans le conteneur ; tout le dépôt est dans /aeac
```

Pour simuler une mission : SITL lancé dans Mission Planner (formation 1), puis `make sim C=<mission>`. Les mocks (manette, détections) se lancent dans un second terminal : `make shell IMG=sim` puis `ros2 run sim_mocks rc_simulator`. Voir [packages/sim_mocks/README.md](packages/sim_mocks/README.md).

`make help` liste toutes les commandes, en trois sections : développement et simulation, test sur véhicule, déploiement. `make check` avant chaque PR.

## Règles du dépôt

- `main` = ce qui vole. On travaille sur une branche, on ouvre une PR, un lead fusionne.
- Le code de mission n'arme jamais et ne change jamais de mode : c'est le pilote. Les seuls nœuds qui le font sont les `*_test` de `sim_mocks`, en simulation.
- Un nom de topic s'écrit une fois, dans `tools/topics.py`. `/aeac/external/...` traverse la radio, `/aeac/internal/...` reste sur le drone.
- Ce qui change entre deux drones, deux terrains ou deux essais est dans `config/`, pas dans le code.
- Code en anglais ; docs, logs et commentaires de haut niveau en français.
- Ce qu'on apprend et qu'on n'a pas le temps de ranger va dans [NOTES.md](NOTES.md).

## Créer un dépôt de mission à partir de ce template

Pour les leads, une fois par dépôt (aeac-2027, suas-2027) :

```bash
cp -r mission-template/ <nouveau-dépôt> && cd <nouveau-dépôt>
git init
for p in custom_interfaces tools nav_stack vision; do git submodule add https://github.com/zenith-polymtl/$p packages/$p; done
git submodule add -b zenith https://github.com/zenith-polymtl/zed-ros2-wrapper packages/zed-ros2-wrapper
make link C=gcs PKG=custom_interfaces && make link C=gcs PKG=tools && make link C=gcs PKG=sim_mocks
make link C=vision PKG=vision && make link C=vision PKG=custom_interfaces
make init && make check
git add -A && git commit -m "init from mission-template"
```

Puis, pour chaque mission : `workspaces/<mission>_ws/src/<mission>_bringup/` (avec `launch/mission.launch.py`), `config/<mission>.yaml`, `make link` des paquets partagés (dont `sim_mocks`, pour que `make shell IMG=sim` trouve les mocks), `gcs_ws/src/gcs_bringup/launch/<mission>.launch.py` pour le sol.

## Sur le drone

Voir [procédure.md](procédure.md) (checklist jour J) et [systemd/install.md](systemd/install.md) (démarrage au boot). Les ports série : `/dev/ttyTHS1` sur JetPack 6, `/dev/ttyTHS0` sur JetPack 5 ; l'utilisateur doit être dans le groupe `dialout`.

## Dépannage

- `ros2 topic list` vide dans un conteneur : vérifier `ROS_DOMAIN_ID` (2 sur le drone, 3 au sol) et que `lo-multicast` est actif sur la Jetson (`make lo-multicast-status`).
- `make build` échoue sur un paquet absent : `make status` ; un sous-module vide se règle avec `make init`, un symlink cassé apparaît dans `make check`.
- Fichiers appartenant à root après un build : les conteneurs tournent en root pour l'instant ; `sudo chown -R $USER:$USER .` dans le dépôt.
- Le reste des problèmes de poste (WSL, Docker, ports) est dans les formations, fichier `DEPANNAGE.md`.
