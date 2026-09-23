# Architecture du dépôt de mission

Une page. Ce qu'il faut savoir avant de lire du code.

## Qui tourne où

| Machine | Régime | Ce qui tourne | Lancé par | Domaine ROS |
|---|---|---|---|---|
| Poste WSL | Développement | conteneur `dev` : coder, construire un workspace, rviz, `ros2 topic` | `make dev` | 3 |
| Poste WSL | Simulation | conteneur `dev` + `mavros-sim` vers le SITL de Mission Planner ; la mission de `C=` avec `sim:=true` ; mocks à la main | `make sim C=` | 3 |
| Jetson | Test sur véhicule | `mavros`, `zed`, `zenoh-air`, `vision`, la mission : les mêmes compose qu'en déploiement, en avant-plan | `make mavros`, `make vision`, `make drone C=` | 2 |
| Jetson | Déploiement | exactement les mêmes compose, démarrés au boot et relancés s'ils tombent | systemd (`make deploy`) | 2 |
| Portable GCS | Vol | conteneur `gcs` (workspace `gcs_ws`) + `zenoh-ground` vers le drone choisi | `make gcs C= DRONE=` | 3 |

**systemd est un emballage.** Tout ce qu'il lance a une cible `make` qui lance la même chose en avant-plan. Pour tester sur le véhicule : `make undeploy`, puis les cibles à la main.

## Ce qui traverse la radio

```
Jetson (domaine 2, DDS local seulement)                 Portable (domaine 3, DDS local seulement)
   nœuds mission ──► /aeac/internal/...   (reste ici)
   nœuds mission ──► /aeac/external/...  ──► zenoh-air ══ SIYI ou Tailscale ══ zenoh-ground ──► nœuds GCS
                     /tf, /tf_static     ──►                                                ──►
```

Trois idées : le nom du topic dit où il voyage ; DDS ne sort jamais d'une machine (`ROS_LOCALHOST_ONLY=1`, d'où le service `lo-multicast` sur la Jetson) ; Zenoh ne porte que ce qui est déclaré externe (listes `allow` de `config/zenoh-air.json5` et `config/drones/*.json5`). Deux domaines différents garantissent qu'un DDS mal configuré ne traverse jamais la radio par accident. Le mode `router` sans découverte automatique évite que deux drones ou deux portables se trouvent par surprise sur le même réseau.

## Plan d'adressage

| Drone | SIYI (lien principal) | Tailscale (secours LTE) | Fichier |
|---|---|---|---|
| Hexa | 192.168.144.30 | 100.87.171.82 | `config/drones/hexa.json5` |
| OS | 192.168.144.31 | 100.64.95.10 | `config/drones/os.json5` |

Un nouveau drone = un fichier de plus dans `config/drones/` et une ligne ici. SSH : `ssh zenith@<adresse>`.

## Une mission

Une mission, c'est trois choses :

1. `workspaces/<mission>_ws/` : ses paquets locaux dans `src/`, et des symlinks vers les paquets partagés de `packages/` (`make link`). Le paquet `<mission>_bringup` contient `launch/mission.launch.py`, lancé sur le drone.
2. `config/<mission>.yaml` : tout ce qui se règle (gains, PWM, interrupteurs, seuils). Le launch le charge et le passe aux nœuds. Rien de tout ça dans le code.
3. `gcs_ws/src/gcs_bringup/launch/<mission>.launch.py` : ce que le portable lance pour cette mission.

`make build C=<mission>` construit ce workspace et rien d'autre. `make sim C=<mission>` le simule. `make drone C=<mission>` le lance sur la Jetson. Le launch est le même en simulation et en vol : `sim:=true` passe un paramètre `sim` aux nœuds qui touchent au matériel, et ils entourent leur seul appel matériel d'un `if not self.sim`. `site:=<nom>` choisit `config/sites/<nom>.yaml` (coordonnées du terrain) ; en simulation, `make sim C=<mission> SITE=<nom>`.

## Règles de code

- **Le code de mission n'arme jamais et ne change jamais de mode.** C'est le pilote. Seuls les nœuds `*_test` de `sim_mocks` le font, sous `sim:=true`, et aucun launch de mission ne les inclut.
- **Un nom de topic s'écrit une fois**, dans `tools/topics.py` : `from tools.topics import SHOOT`. Jamais de littéral dans un nœud ni un launch.
- **Un enum, une constante de message** dans `custom_interfaces` (états, modes, PWM). Jamais redéfini dans un nœud.
- **Pas de `time.sleep` dans un callback, pas de `spin_until_future_complete` depuis un callback.** Timers et `call_async`.
- **Pas de vérification factice.** Une fonction de readiness vérifie ou n'existe pas.
- **Logs en français**, `INFO` pour les événements (jamais du périodique), `WARN` pour ce qui demande un regard, `ERROR` pour ce qui arrête. Code, topics, commits en anglais.
- **`package.xml` est le contrat** : toute dépendance y est déclarée. Le Dockerfile installe ce que `rosdep` ne couvre pas et le dit en commentaire.
- **Pas de tests, pas de dossier `test/`.** `make check` vérifie ce qui se vérifie sans en écrire.

## Sous-modules, en trois phrases

On clone avec `--recurse-submodules`. `make init` rattrape si on a oublié. Si `make status` dit qu'un sous-module est modifié localement, on demande à un lead avant de continuer.

## Pour les leads

- **Avancer un paquet partagé** : `make bump PKG=tools` (fetch, checkout de `origin/main`, tag daté, pointeur stagé), puis `git commit -m "bump tools"` et `git push --recurse-submodules=on-demand`.
- **Contribuer à un paquet partagé** : `git -C packages/tools switch main`, coder, commit, push, PR dans le dépôt du paquet, puis `make bump PKG=tools` ici.
- **Créer un paquet partagé** : dépôt GitHub avec `package.xml` à la racine, `git submodule add <url> packages/<nom>`, une ligne dans `packages/README.md`.
- **Sortir un paquet du partage** : `git submodule deinit packages/<nom>`, copier le dossier dans le workspace concerné, `git rm packages/<nom>`.
- **Déployer** : `make deploy C=<mission>` sur la Jetson (voir `systemd/install.md`).
- **Après la compétition** : tag `<compétition>-<année>` sur `main`, puis suppression des workspaces et paquets de mission qui ne serviront plus.
- **Modèles de vision** : `models/` est ignoré par git ; `make models` télécharge l'archive dont l'URL est dans le Makefile (`MODELS_URL`).
