# Exploration : Dockerfiles et dépendances Python

> **Décision (Colin, 21 septembre 2026)** : D1 + R1. Un Dockerfile complet par rôle, dépendances Python en `pip install` en ligne comme en 2026, plus simple pour les nouveaux et ça marche. Pas de fichier requirements. Intégré dans `PLAN-ARCHITECTURE-aeac-2027-v3.md`, P7.

*21 septembre 2026. Répond à la réserve de Colin sur P7 de la V1 du plan : « enlever requirements.txt, je ne suis pas sûr ; comparer avec comment c'est fait dans aeac-2026 ». Précision d'abord : la V1 disait « le requirements.txt est lu par le Dockerfile ou n'existe pas », c'est-à-dire l'un ou l'autre, pas « supprimer ». En 2026, le fichier existe et n'est lu par personne, ce qui est le pire des deux. Ce document compare les façons d'organiser les images et les dépendances.*

---

## 1. Ce que fait la branche de compétition

Vérifié sur `origin/mission-2-photo-pipeline` (`71408c4`), dossier `docker/`.

| Fichier | Lignes | Base | Ce qu'il ajoute | Utilisé par |
|---|---|---|---|---|
| `dockerfile.dev` | 78 | `ros:humble-ros-base` | mavros + GeographicLib, `nlohmann-json3-dev`, pip `google-api-python-client` (upload Drive), rviz2, rqt, x11-apps, image-transport | `dev.yml` (poste WSL, GCS) |
| `dockerfile.payload` | 60 | `ros:humble-ros-base` | mavros + GeographicLib, `ros-humble-zed-msgs` | `payload.yml` (Jetson) |
| `dockerfile.water` | 63 | `ros:humble-ros-base` | mavros + GeographicLib, pip `numpy<1.24 ultralytics`, `cv-bridge` | `water.yml` (Jetson) |
| `dockerfile.mavros` | 26 | `ros:humble-ros-base` | mavros + GeographicLib | `mavros.yml` (service Jetson) |
| `dockerfile.vision` | 100 | `nvcr.io/nvidia/l4t-jetpack:r36.4.0` | ROS Humble installé à la main, `numpy==1.26.4` épinglé deux fois (dont un `--force-reinstall` final), `ultralytics --no-deps`, `cv-bridge`, `zed-msgs`, TensorRT du JetPack | `vision.yml` (Jetson, GPU) |
| `requirements_v1.txt` | 206 | | `pip freeze` de la Jetson (paquets ROS, ament, tout) | Personne |

Constats :

- **Les quatre images ROS partagent une cinquantaine de lignes identiques** (base, locale, outils colcon, mavros, GeographicLib, utilisateur `dev`). `diff dockerfile.dev dockerfile.payload` ne montre que les extras de `dev`. C'est le « presque identiques et c'est assumé » de la revue.
- **Les dépendances Python sont dans des `RUN pip install` en ligne**, différentes par image, sans liste lisible. La divergence `numpy<2` / `numpy<1.24` / `numpy==1.26.4` vient de là : trois fichiers, trois valeurs, aucune vue d'ensemble.
- **`dockerfile.vision` est un autre monde** : base JetPack, ROS installé à la main, épinglages fragiles, ne se construit que sur la Jetson (ARM, CUDA). Il ne partagera jamais de lignes avec les autres et c'est normal.
- **`requirements_v1.txt` est un instantané**, pas une intention : il liste `ament-cmake-test==1.3.14` et 200 autres lignes qu'on ne veut pas réinstaller par pip. Il ne peut pas servir tel quel.
- **Pas de `.dockerignore`** : chaque build envoie tout le dépôt (modèles, PNG, `.git`) au démon.

---

## 2. Deux questions distinctes

**Q1. Comment organiser les images** pour que « presque identiques » ne redevienne pas « divergentes par accident » ?
**Q2. Où écrire les dépendances Python** pour qu'elles soient lisibles, comparables entre images, et lues par le build ?

---

## 3. Q1 : organisation des images

### D1 : un Dockerfile complet par rôle (2026, et V1 du plan)

`dockerfile.drone`, `dockerfile.gcs`, `dockerfile.mavros`, `dockerfile.vision`, chacun autonome. En-tête de trois lignes « ce qui diffère et pourquoi ».
- Simple à lire un par un ; c'est ce que la formation 2 montre.
- La duplication de 50 lignes reste, et rien n'empêche qu'elle diverge. L'en-tête est une promesse, pas une garantie.

### D2 : un Dockerfile multi-étapes pour la famille ROS, un fichier à part pour vision

Un seul `docker/dockerfile.ros` avec des étapes nommées ; chaque compose choisit la sienne par `target:`.

```dockerfile
FROM ros:humble-ros-base AS base
# tout ce qui est commun : locale, colcon, mavros, GeographicLib, cyclonedds, utilisateur

FROM base AS mavros
# rien de plus : l'image mavros, c'est base

FROM base AS drone
COPY docker/requirements-drone.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-drone.txt
RUN apt-get install -y ros-humble-zed-msgs

FROM drone AS gcs
COPY docker/requirements-gcs.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-gcs.txt
RUN apt-get install -y ros-humble-rviz2 ros-humble-rqt x11-apps
```

```yaml
# compose/gcs.yml
build:
  context: ..
  dockerfile: docker/dockerfile.ros
  target: gcs
```

- Le commun est écrit une fois ; chaque étape ne contient que ce qui lui est propre, donc **la différence entre deux images est le texte de l'étape**, plus besoin d'en-tête qui l'explique.
- Docker partage les couches de `base` entre les images : moins de disque, et un changement dans `drone` ne reconstruit pas `base`.
- `docker compose build` gère le `target` : aucune commande nouvelle, aucun ordre de build à respecter.
- `dockerfile.vision` reste un fichier séparé, base JetPack, avec son propre `requirements-vision.txt`.
- Coût : un concept de plus (les étapes) pour qui lit le Dockerfile. La formation 2 n'en parle pas ; la formation 5 le dit en deux phrases (« chaque `FROM ... AS` est une image ; le compose choisit laquelle »).

### D3 : image de base publiée, puis Dockerfiles courts `FROM zenith/ros-base`

Comme D2 mais la base est une image construite à part et poussée sur un registre.
- Refusé : il faut un registre (GHCR) et un ordre de build ; c'est de l'infrastructure de plus pour des recrues, et Zenith n'en a pas.

---

## 4. Q2 : dépendances Python

### R1 : `pip install` en ligne dans les `RUN` (2026)

- Aucun fichier à part ; mais illisible, non comparable, et c'est ce qui a produit trois versions de `numpy`.

### R2 : un `requirements-<rôle>.txt` par image, copié et lu par le Dockerfile

`docker/requirements-drone.txt`, `requirements-gcs.txt` (les extras de la GCS seulement, puisque `gcs` hérite de `drone` en D2), `requirements-vision.txt`.
- Lisible : `cat` suffit pour savoir ce qu'une image contient en Python ; `diff` entre deux fichiers dit ce qui diffère.
- Lu par le build, donc vrai par construction. Un fichier qui n'est pas dans un `COPY` du Dockerfile n'a pas le droit d'exister dans `docker/`.
- Épinglage : les versions sont épinglées (`numpy==1.26.4`) quand une raison existe, et la raison est en commentaire sur la ligne. Sinon pas d'épinglage.
- Cache Docker : un changement de dépendance Python ne reconstruit que la couche `pip`, pas les couches apt au-dessus.

### R3 : `rosdep` depuis les `package.xml`

La voie officielle ROS : chaque paquet déclare `<exec_depend>python3-numpy</exec_depend>`, le Dockerfile fait `rosdep install --from-paths src`.
- Cohérent avec « `package.xml` est le contrat » (P13).
- Mais `rosdep` ne connaît que les paquets apt (`python3-numpy` d'Ubuntu, pas `numpy==1.26.4` de pip), ne sait rien de `ultralytics`, et sur la Jetson les paquets apt de numpy et d'OpenCV sont précisément ceux qu'on veut éviter. Ça marcherait pour la GCS, pas pour vision. Deux mécanismes au lieu d'un.
- À garder pour les dépendances apt ROS (`ros-humble-cv-bridge` déclaré dans le `package.xml` de `vision`), pas pour Python.

---

## 5. Comparaison

| Critère | D1 + R1 (2026) | D1 + R2 | D2 + R2 (proposé) |
|---|---|---|---|
| Fichiers dans `docker/` | 5 Dockerfiles + un freeze mort | 4 Dockerfiles + 3 requirements | 2 Dockerfiles (`ros`, `vision`) + 3 requirements |
| Lignes dupliquées | ~150 | ~150 | 0 |
| Savoir ce qui diffère entre drone et gcs | Lire deux fichiers de 60 lignes | Lire deux fichiers et deux requirements | Lire une étape de 6 lignes |
| Risque de divergence accidentelle | Élevé (démontré) | Moyen (les Dockerfiles peuvent encore diverger) | Faible (le commun n'existe qu'une fois) |
| Disque sur la Jetson | Trois images complètes | Trois images complètes | Couches de base partagées |
| Notion nouvelle pour une recrue | Aucune | Aucune | Étapes nommées, deux phrases |
| Compatible avec « un par machine, presque identiques » | Oui | Oui | Oui : une étape par machine, presque vides |

---

## 6. Recommandation

**D2 + R2**, avec `vision` à part : `docker/dockerfile.ros` (étapes `base`, `mavros`, `drone`, `gcs`), `docker/dockerfile.vision`, trois `requirements-*.txt` lus par les builds, `requirements_v1.txt` supprimé, et un `.dockerignore`. La décision « un Dockerfile par machine » de la revue est respectée dans l'esprit : chaque machine a son étape, et les différences sont là où on les lit.

Si les étapes nommées paraissent une notion de trop, D1 + R2 est le repli : quatre fichiers autonomes, mais au moins les dépendances Python deviennent lisibles et lues.

Ce que le plan V2 retient pour P7 : D2 + R2 proposé, D1 + R2 en repli, à trancher.

## 7. Questions pour la discussion

- L'image `gcs` hérite-t-elle de `drone` (tout ce que le drone a, plus rviz et rqt) ou de `base` (seulement ce dont la GCS a besoin) ? Hériter de `drone` permet de simuler n'importe quelle mission sur le poste WSL avec l'image `gcs` ; c'est plus gros mais plus simple.
- Le client Google Drive de `dockerfile.dev` (upload d'images en compétition) : dépendance de la GCS 2027 ou spécifique à la mission 2 de 2026 ?
- `dockerfile.vision` : le remettre au propre (un seul épinglage de numpy, commentaires sur chaque contrainte) fait-il partie du template ou du chantier « vision plus versatile » ?
