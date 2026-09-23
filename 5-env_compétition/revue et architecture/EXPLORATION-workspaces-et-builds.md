# Exploration : workspaces, montage des conteneurs et taille des builds

> **Décision (Colin, 21 septembre 2026)** : W1. Le temps de build est important. Pas de `dev_ws` : `gcs_ws` sert de workspace de développement, comme en 2026, et le conteneur de dev monte le dépôt entier pour construire et lancer n'importe quel workspace. Pas de workspace `sim` à part. Intégré dans `PLAN-ARCHITECTURE-aeac-2027-v3.md`, P6 et P11 à P14.

*21 septembre 2026. Répond aux réserves de Colin sur P6 et P11 à P14 de la V1 du plan : « le but des workspaces séparés est de limiter les temps de build et de ne pas avoir plus de paquets que nécessaire ; tout réunir et monter tout le dépôt me semble plus lourd ; je préfère une mission = un workspace, comme en 2026, mais je suis ouvert si on compare ». Ce document compare trois façons de faire, mesure ce qui coûte vraiment, et propose une solution qui garde « une mission = un workspace ».*

---

## 1. Ce que fait vraiment la branche de compétition

Vérifié le 21 septembre sur `origin/mission-2-photo-pipeline` (`71408c4`).

**Les symlinks sont déjà dans git.** `git ls-tree` sur `workspaces/water_ws/src/` montre `bringup`, `custom_interfaces`, `nav_stack`, `polar_system`, `tools` en mode `120000` (symlink versionné, cible `../../../packages/tools`), et `control_nav`, `gimbal_controller`, `state_w`, `shoot_and_capture`, `water_payload`, `remote_controller_interface` en dossiers. Même chose dans `payload_ws` et `ground_station_ws`. Autrement dit, la liste des paquets partagés d'un workspace est déjà versionnée sous la forme la plus simple qui soit : `ls src/`.

**Deux autres listes disent la même chose.** `pkgs.txt` (lu par `link_ws.sh`, qui recrée les symlinks que git a déjà) et les bind-mounts paquet par paquet de `water.yml`, `payload.yml`, `vision.yml` (qui recouvrent les symlinks dans le conteneur parce que celui-ci ne monte que le workspace, donc `../../../packages` n'existe pas dedans). Trois listes, trois endroits où oublier un paquet. Le symptôme relevé dans la revue (`polar_system` dans `pkgs.txt` mais absent de `payload_ws/src`) vient de là.

**Tailles réelles.** `water_ws` : 11 paquets (5 partagés, 6 locaux). `payload_ws` : 10 (5 partagés, 5 locaux). `ground_station_ws` : 5. `vision_ws` : `bringup` seul dans git, `vision` et `custom_interfaces` arrivent par bind-mount. Total distinct dans le dépôt : environ 20 paquets maison.

---

## 2. Ce qui coûte, et ce qui ne coûte pas

Pour trancher sur des faits plutôt que sur une impression de lourdeur.

| Élément | Coûte quoi | Dépend de |
|---|---|---|
| **Bind-mount du dépôt entier** (`..:/aeac`) au lieu du seul workspace | Rien. Un bind-mount est une vue du système de fichiers de l'hôte : aucune copie, aucune RAM, aucun CPU, quelle que soit la taille du dossier. `dev.yml` le fait déjà depuis 2025 sans effet mesurable. | Rien |
| **Découverte colcon** (lecture des `package.xml` sous `src/`) | Quelques dizaines de millisecondes pour 20 paquets. | Nombre de `package.xml`, pas leur taille |
| **Temps de build colcon** | Le vrai coût. Pour des paquets `ament_python`, quelques secondes par paquet (copie des sources dans `install/`) ; pour un paquet C++ comme les serveurs web, de 30 s à quelques minutes. | **Le nombre de paquets sélectionnés pour le build**, et rien d'autre |
| **Contexte de build Docker** (`context: ..` dans tous les compose) | Réel et déjà payé aujourd'hui : à chaque `docker compose build`, Docker envoie tout le dépôt au démon, y compris les 68 Mo de modèles et les images PNG. C'est ce qui rend `make build` lent au premier essai. | Un `.dockerignore` (absent en 2026). Indépendant du choix de workspace. |
| **Dossiers `build/` et `install/`** | Disque seulement, de l'ordre de 50 à 200 Mo par workspace. | Un par workspace ou par conteneur |

Conclusion de ce tableau : **monter tout le dépôt ne rend rien plus lourd**, et la seule chose qui allonge un build est la liste des paquets construits. La question devient donc uniquement : comment cette liste est-elle définie, et par quoi une recrue la voit-elle ?

---

## 3. Trois options

### Option W1 : une mission = un workspace, symlinks versionnés, un seul montage

C'est l'état réel de la branche, débarrassé de ses deux listes redondantes.

```
workspaces/
├── water_ws/src/
│   ├── tools -> ../../../packages/tools            symlink commis
│   ├── nav_stack -> ../../../packages/nav_stack    symlink commis
│   ├── custom_interfaces -> ../../../packages/custom_interfaces
│   ├── water_bringup/                              dossier local
│   └── gimbal_controller/                          dossier local
├── payload_ws/src/ ...
├── vision_ws/src/
│   ├── vision -> ../../../packages/vision
│   ├── custom_interfaces -> ../../../packages/custom_interfaces
│   └── vision_bringup/
└── gcs_ws/src/ ...
```

- Tous les compose montent le dépôt entier dans `/aeac` (comme `dev.yml`) et mettent `working_dir: /aeac/workspaces/$(C)_ws`. Les symlinks relatifs résolvent sur l'hôte et dans le conteneur. Plus de bind-mount paquet par paquet.
- `pkgs.txt` et `link_ws.sh` disparaissent : git porte les symlinks. Ajouter un paquet partagé à une mission = `make link C=water PKG=polar_system` (un `ln -s` relatif, puis on commet le lien), ou à la main.
- `make build C=water` = `cd workspaces/water_ws && colcon build`. Tout le workspace, rien d'autre : c'est exactement la sémantique 2026, et le `Makefile` 2026 le fait déjà avec `WS_REL := workspaces/$(C)_ws`.
- Chaque workspace a ses `build/` et `install/`, donc deux conteneurs d'images différentes (drone et vision) ne se marchent pas dessus.
- Un paquet local à une mission vit dans `workspaces/<mission>_ws/src/`, comme en 2026. Un paquet partagé vit dans `packages/`, et apparaît dans les workspaces qui le lient.

**Ce qu'une recrue voit** : `ls workspaces/water_ws/src` dit quels paquets la mission utilise ; les flèches de `ls -l` disent lesquels sont partagés. Aucun fichier de liste à connaître.

**Pièges** : les symlinks dans git demandent que le dépôt soit cloné sous WSL, pas sous Windows (règle déjà posée par la formation 2). Un symlink cassé (paquet renommé) donne un dossier vide que colcon ignore en silence ; `make check` doit le détecter.

### Option W2 : un seul workspace, la mission choisit par `package.xml` (V1 du plan)

`ws/src -> packages/`, `make build C=water` = `colcon build --packages-up-to water_bringup --build-base build/water --install-base install/water`. Le jeu de paquets construits est le même qu'en W1 si les `package.xml` sont justes.

**Avantages** : aucun symlink, aucune liste ; la dépendance est déclarée là où ROS la veut.
**Inconvénients** relevés par Colin, et fondés : la liste est abstraite (il faut lire un `package.xml` pour savoir ce qu'une mission construit) ; un `colcon build` tapé sans argument construit tout, y compris ce qui ne se construit pas sur cette machine ; les `build/<C>` par mission sont une notion de plus ; ce n'est pas ce que 2026 a fait, donc pas de parallèle possible dans la formation.

### Option W3 : 2026 tel quel

Garder `pkgs.txt`, `link_ws.sh`, et les bind-mounts par paquet. Refusé par la revue (deux mécanismes, trois listes) et rien ne plaide pour.

---

## 4. Comparaison

| Critère | W1 symlinks versionnés | W2 un workspace | W3 2026 |
|---|---|---|---|
| Paquets construits pour `water` | Ceux de `water_ws/src` (11) | Les dépendances de `water_bringup` (11 si `package.xml` juste) | 11 |
| Temps de build | Identique | Identique | Identique |
| Ressources du conteneur | Identiques (bind-mount gratuit) | Identiques | Identiques |
| Où une recrue voit la liste | `ls src/` | `package.xml` du bringup | `pkgs.txt`, ou le compose, ou `src/` (les trois peuvent diverger) |
| Ajouter un paquet partagé à une mission | `make link` + commit du lien | Une ligne dans `package.xml` | `pkgs.txt` + `make link` + éditer le compose |
| Créer un paquet local | `ros2 pkg create` dans `src/` | `ros2 pkg create` dans `packages/` + `package.xml` du bringup | `ros2 pkg create` dans `src/` |
| Erreur silencieuse possible | Symlink cassé (détectable par `make check`) | Dépendance oubliée dans `package.xml` : le paquet n'est pas construit, `ros2 launch` échoue au lancement (bruyant) | Listes divergentes |
| `colcon build` sans argument | Construit la mission, comme attendu | Construit tout | Construit la mission |
| Notions à enseigner | Symlink, un workspace par mission (déjà en formation 3) | `--packages-up-to`, `--build-base` | pkgs.txt, link script, bind-mounts |
| Parallèle avec 2026 en formation | Direct : « voilà 2026 sans les deux listes en trop » | Rupture | Identique |
| Scripts maison | Aucun (`make link` est un `ln -s`) | Aucun | `link_ws.sh` |

---

## 5. Recommandation

**W1.** Elle respecte « une mission = un workspace », garde la sémantique de build de 2026 (petit build par mission, un `build/` par workspace), et supprime ce qui a cassé (deux listes redondantes, deux mécanismes de montage). Le seul changement visible par rapport à la branche est que les compose de mission montent le dépôt entier comme `dev.yml` le fait déjà, et que `pkgs.txt` et `link_ws.sh` sont retirés puisque git fait leur travail.

À ajouter en même temps, indépendamment de l'option : un `.dockerignore` (`models/`, `**/build/`, `**/install/`, `**/log/`, `*.png`, `.git/`) pour que `make build` ne renvoie plus tout le dépôt au démon Docker. C'est probablement la lourdeur ressentie.

Ce que le plan V2 retient en conséquence (P6, P11 à P14 réécrits) :

1. `workspaces/<mission>_ws/` par mission, plus `gcs_ws` et `vision_ws`. `C=<mission>` sélectionne compose et workspace, comme dans le Makefile 2026.
2. Symlinks relatifs commis dans `src/` pour les paquets partagés ; `make link C= PKG=` les crée ; `make check` détecte les liens cassés.
3. Tous les compose montent `..:/aeac` ; `working_dir` sur le workspace de `C`. Plus de bind-mount par paquet.
4. `make build C=` = `colcon build` dans le workspace, sans option.
5. Un paquet est local (dans `src/`) sauf s'il sert à deux workspaces ou à deux dépôts, auquel cas il va dans `packages/` (sous-module s'il sert à deux dépôts, dossier simple s'il ne sert qu'à deux workspaces du même dépôt).

## 6. Questions pour la discussion

- Un paquet partagé entre deux workspaces du même dépôt mais pas entre dépôts (par exemple `remote_controller_interface`) : dossier simple dans `packages/` (proposé) ou sous-module quand même, pour n'avoir qu'une règle ?
- `dev_ws` : faut-il un workspace de développement qui lie tout, pour rviz et les essais, ou le développement se fait-il dans le workspace de la mission avec l'image `dev` ?
- Le workspace `sim` : la simulation d'une mission se fait dans le workspace de cette mission (`make sim C=water`), il n'y a pas de workspace `sim` à part. À confirmer.
