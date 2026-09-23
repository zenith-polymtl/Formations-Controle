# Plan d'implémentation : `mission-template/` puis `aeac-2027`

> Spec : `PLAN-ARCHITECTURE-aeac-2027-v3.md` (approuvée le 21 septembre 2026). Ce plan découpe l'étape 2 (squelette), l'étape 3 (simulation, partie template) et l'étape 6 (création d'aeac-2027) de sa section 14. L'étape 1 (dépôts partagés) est reportée par Colin.

**But** : un dossier `mission-template/` exécutable, copié tel quel pour créer `aeac-2027`, avec le moins de concepts possible pour une recrue.

**Contraintes globales** (copiées de la V3) : une mission = un workspace, symlinks vers `packages/` ; un Dockerfile complet par rôle, pip en ligne ; Makefile en trois sections ; systemd jamais seule voie ; `sim:=true` ne fait que passer un paramètre ; SITL Mission Planner ; code EN, docs et logs FR ; pas de tests ; root dans les conteneurs ; `ROS_DOMAIN_ID` 2 drone, 3 sol ; Zenoh `router`, `ROS_LOCALHOST_ONLY=1` sur le drone et la GCS en vol.

**Contrainte de poste** : ce poste Windows ne peut pas créer de symlinks natifs. Le template ne contient donc pas de symlinks ; la recette « créer un dépôt de mission » du README les crée avec `make link` (sous WSL), et pour aeac-2027 le sous-agent les crée comme entrées git de type symlink (`git update-index --cacheinfo 120000`), qui deviennent de vrais liens au clone sous WSL.

## Fichiers et responsabilités

| Fichier | Responsabilité |
|---|---|
| `Makefile` | Trois sections ; `C=` mission, `IMG=` conteneur, `DRONE=` config sol |
| `compose/dev.yml`, `sim.yml`, `drone.yml`, `vision.yml`, `gcs.yml`, `mavros.yml`, `zed.yml`, `zenoh-air.yml`, `zenoh-ground.yml` | Un service par fichier ; tous montent `..:/aeac` |
| `docker/dockerfile.drone`, `gcs`, `vision`, `mavros` | Une image par rôle, autonome, en-tête « ce qui diffère » |
| `config/mavros.yaml`, `zenoh-air.json5`, `drones/hexa.json5`, `drones/os.json5`, `sites/sim.yaml`, `README.md` | Ce qui change par mission, site, drone |
| `packages/sim_mocks/` | `rc_simulator`, `target_mock`, `takeoff_test` |
| `packages/README.md` | Les cinq sous-modules et la règle local / partagé |
| `workspaces/gcs_ws/src/gcs_bringup/` | Launch `base.launch.py` (heartbeat GCS) ; une mission ajoute `<mission>.launch.py` |
| `workspaces/vision_ws/README.md` | Liens à créer (vision, custom_interfaces), bringup vision à venir |
| `scripts/check.py` | `make check` |
| `systemd/*.service`, `install.md` | Déploiement Jetson, `__REPO__` remplacé par `make deploy` |
| `README.md`, `ARCHITECTURE.md`, `NOTES.md`, `procédure.md`, `.gitignore`, `.dockerignore` | Documentation et hygiène |

## Tâches

### Tâche 1 : Makefile, compose, Dockerfiles, hygiène
- [ ] Écrire les fichiers listés. Vérification : `make -n help build sim drone gcs deploy` ne renvoie aucune erreur de syntaxe ; `docker compose -f compose/<x>.yml config` valide chaque compose (si Docker est disponible sur le poste, sinon relecture).

### Tâche 2 : config et systemd
- [ ] Écrire `config/` et `systemd/`. Vérification : chaque json5 est valide (parse `json5` en Python ou relecture) ; chaque unité a `WorkingDirectory=__REPO__` et un `ExecStart` qui correspond à une cible `make` de la section 2.

### Tâche 3 : `sim_mocks`, `gcs_bringup`, `check.py`
- [ ] Écrire les paquets et le script. Vérification : `python scripts/check.py` s'exécute sur le template et ne signale que les sous-modules absents ; `python -m py_compile` sur chaque `.py`.

### Tâche 4 : documentation
- [ ] `README.md` (quick start puis recette « créer un dépôt de mission »), `ARCHITECTURE.md`, `NOTES.md`, `procédure.md`. Vérification : chaque `make <cible>` cité existe dans le Makefile (c'est ce que `check.py` vérifie).

### Tâche 5 : créer `aeac-2027` (sous-agent)
- [ ] Copier `mission-template/` dans `C:\Users\colin\Zenith\aeac-2027` (dépôt git existant, README seul), ajouter les cinq sous-modules (`git submodule add`), créer les entrées symlink dans `gcs_ws/src` (custom_interfaces, tools) et `vision_ws/src` (vision, custom_interfaces), `git add`, un commit local, pas de push. Vérification : `git ls-tree HEAD workspaces/gcs_ws/src/` montre des entrées `120000` ; `git submodule status` liste cinq lignes.
