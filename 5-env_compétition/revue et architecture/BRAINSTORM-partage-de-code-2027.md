# Partage de code maison : options pour aeac-2027

*Brainstorm du 21 septembre 2026, en préparation du plan d'architecture aeac-2027. Question posée : comment partager des paquets ROS 2 maison entre les workspaces d'un même dépôt et entre plusieurs années ou dépôts (aeac-2027, SUAS 2027, VTOL), sans retomber dans la complexité constatée dans la revue pédagogique d'aeac-2026. Décisions déjà prises : squelette générique seulement dans le template, code en anglais et docs en français, template dans `Control-Formations/5-env_compétition/mission-template/`.*

---

## 0. Le besoin, reformulé

Il y a en réalité trois besoins distincts, que 2026 a traités avec trois mécanismes empilés :

| Besoin | Mécanisme 2026 | Ce qui a cassé |
|---|---|---|
| **B1. Partager entre missions d'un même dépôt** (le paquet `tools` sert à `payload`, `water` et la GCS) | `pkgs.txt` + `link_ws.sh` (symlinks), doublé par les bind-mounts un par un dans `payload.yml` et `water.yml` | Deux sources de vérité ; `polar_system` listé mais jamais lié ; chemins différents selon le conteneur (`/aeac/workspaces/water_ws` vs `/water_ws`) |
| **B2. Partager entre machines** (le drone n'a pas besoin des serveurs web, la GCS n'a pas besoin de la ZED) | Un workspace par mission, chacun avec sa liste | Trois workspaces à expliquer, `dev_ws` annoncé mais absent |
| **B3. Partager entre années ou dépôts** (réutiliser `nav_stack` en 2027) | Sous-modules Git (8, dont un tiers) | Pointeurs qui dérivent (`ensure_submodules.sh --remote`), `.gitmodules` contredit par le checkout local, nesting `nav_stack/nav_stack/nav_stack/`, detached HEAD incompris |

Le constat clé de la revue : **en 2026, personne n'a profité du partage par pointeur.** Deux personnes ont fait 281 commits sur 288, toujours depuis le même dépôt. Les sous-modules ont coûté (dérive, confusion) sans rapporter (aucun autre dépôt ne consommait `nav_stack`). Ça ne veut pas dire que le besoin B3 est faux pour 2027 : SUAS 2027 arrive en parallèle, et le VTOL pourrait vouloir `tools`. Ça veut dire que le mécanisme doit coûter presque rien tant que le besoin ne se matérialise pas.

Un principe qui simplifie tout, quelle que soit l'option retenue : **B1 et B2 disparaissent si on n'a qu'un seul workspace.** ROS 2 a déjà un mécanisme pour « quels paquets cette mission utilise » : les dépendances du `package.xml`. `colcon build --packages-up-to water_bringup` construit `water_bringup` et tout ce dont il dépend, rien d'autre. La liste de paquets d'une mission, c'est la balise `<exec_depend>` de son paquet bringup. Un nouveau apprend ça de toute façon en formation 3.

Les trois options ci-dessous partent donc toutes d'un seul workspace et ne diffèrent que sur B3.

---

## 1. Option A : monorepo, un seul workspace, partage inter-années par copie ou par continuité

### Structure

```
aeac-2027/
├── Makefile
├── compose/            drone.yml, gcs.yml, mavros.yml, zenoh-air.yml, zenoh-ground.yml, sim.yml
├── docker/             dockerfile.drone, dockerfile.gcs
├── config/             <mission>.yaml, zenoh-*.json5, mavros.yaml
├── packages/           tous les paquets ROS 2 maison, à plat
│   ├── custom_interfaces/
│   ├── tools/          (topics.py, heartbeats)
│   ├── nav_stack/
│   ├── sim_mocks/      (rc_simulator, target_mock)
│   ├── water_bringup/  (launch + dépendances de la mission water)
│   └── ...
├── ws/
│   └── src -> ../packages     (un seul symlink, commis dans git)
├── systemd/
├── ARCHITECTURE.md
└── procédure.md
```

Un seul sous-module toléré : le code tiers qu'on ne modifie pas ou presque (`zed-ros2-wrapper`, fork `zenith`), et il ne vit même pas dans `ws/src` puisque la ZED tourne dans son propre conteneur.

### Ce que fait un nouveau

| Action | Commandes |
|---|---|
| Jour 1 | `git clone`, `make build C=sim`, `make sim`. Aucune étape d'initialisation. |
| Ajouter un paquet | `ros2 pkg create` dans `packages/`, l'ajouter en `<exec_depend>` du bringup de sa mission. Rien d'autre à éditer. |
| Modifier `tools` | Éditer, tester, commit, PR. Un seul git, un seul `git status`. |
| Construire pour la GCS | `make build C=gcs`, qui fait `colcon build --packages-up-to gcs_bringup`. |

### Partage inter-années, deux variantes

**A1, copie.** Quand aeac-2028 démarre, on copie `packages/nav_stack/` dans le nouveau dépôt. Pas d'historique, pas de lien. Si une correction est faite dans un dépôt, on la reporte à la main dans l'autre. C'est ce que 2026 a fait de facto pour `control_nav` (deux copies, l'une périmée), donc le risque est réel, mais il est visible et compréhensible par n'importe qui.

**A2, continuité.** Le dépôt ne s'appelle plus par l'année. Un dépôt `missions` (ou `aeac-2027` gardé tel quel puis renommé) traverse les années : un tag `aeac-2027` au moment de la compétition, puis on continue dessus. Une mission SUAS 2027 est un `suas_bringup` de plus dans le même `packages/`, un `C=suas` de plus dans le Makefile. L'historique est préservé, il n'y a rien à copier. Le prix : le dépôt accumule des paquets morts, et il faut une purge après chaque PODR (supprimer les bringup et paquets de mission qui ne serviront plus). Le nom de dépôt `aeac-2026` a déjà montré la limite du nommage par année : on a hésité à y mettre autre chose.

### Implications

- **Complexité enseignée** : clone, `package.xml`, `--packages-up-to`. Trois notions, dont deux déjà en formation 3.
- **Un seul `git status`**, un seul historique, `git blame` fonctionne sur tout.
- **Le template reste vrai** : le dossier `mission-template/` dans Control-Formations a exactement cette structure, et aeac-2027 en est une copie. Aucun mécanisme dans le template ne dépend d'un dépôt externe.
- **Ce qu'on perd** : un paquet corrigé dans aeac-2027 ne se propage pas à SUAS 2027 si SUAS est un autre dépôt (A1). Avec A2, il n'y a rien à propager.
- **Risque A2** : un dépôt unique et vivant demande une discipline de branche (`main` = ce qui vole) qui a déjà manqué en 2026. Mais ce risque existe dans toutes les options.
- **Cas limite** : un paquet lourd à construire ou à dépendances exotiques (CUDA, TensorRT) dans `packages/` ralentit `colcon` sur la GCS ? Non, tant qu'aucun bringup GCS n'en dépend, `--packages-up-to` ne le touche pas. Si un jour il faut l'exclure de la découverte, un fichier `COLCON_IGNORE` dans son dossier suffit.

**Effort de mise en place** : environ 2 h pour le squelette (Makefile, symlink, compose), aucun script maison.

---

## 2. Option B : paquets partagés dans des dépôts séparés, importés par un fichier `.repos` (vcstool)

C'est la façon standard dans l'écosystème ROS de composer un workspace à partir de plusieurs dépôts (ros2.repos, navigation2, MoveIt utilisent ça). L'outil `vcs` (paquet `python3-vcstool`) lit un YAML et clone chaque entrée à la version demandée.

### Structure

```
aeac-2027/
├── deps.repos              la liste des paquets partagés, avec leur version
├── packages/               paquets spécifiques à ce dépôt (suivis par git)
│   └── water_bringup/
├── packages/shared/        rempli par `vcs import`, dans .gitignore
│   ├── custom_interfaces/
│   ├── tools/
│   └── nav_stack/
└── ws/src -> ../packages
```

```yaml
# deps.repos
repositories:
  packages/shared/custom_interfaces:
    type: git
    url: https://github.com/zenith-polymtl/custom_interfaces
    version: v2027.1
  packages/shared/tools:
    type: git
    url: https://github.com/zenith-polymtl/tools
    version: v2027.1
```

### Ce que fait un nouveau

| Action | Commandes |
|---|---|
| Jour 1 | `git clone`, `make deps` (fait `vcs import packages/shared < deps.repos`), `make build C=sim`. Une étape de plus qu'en A. |
| Ajouter un paquet de mission | Comme en A, dans `packages/`. |
| Modifier `tools` | `cd packages/shared/tools`, branche, commit, push, PR **dans le dépôt tools**, puis changer `version:` dans `deps.repos` et commit **dans aeac-2027**. Deux dépôts, deux PR. |
| Mettre à jour les partagés | `make deps` relit `deps.repos` ; `vcs pull` prend la tête de la branche si `version:` est une branche. |

### Implications

- **Le pin est lisible** : un YAML avec `version:` remplace le pointeur binaire de sous-module. Un nouveau voit ce qui est épinglé sans commande git.
- **Pas de detached HEAD dans le superprojet**, pas de `.gitmodules` qui ment : `packages/shared/` est simplement ignoré par le git d'aeac-2027.
- **Le piège principal** : `git status` d'aeac-2027 ne voit pas les modifications dans `packages/shared/`. Une recrue qui édite `tools` et fait `git commit -a` à la racine ne commet rien et ne le sait pas. C'est le même problème que les sous-modules sous une autre forme, et il faut un garde-fou (une cible `make status` qui fait `vcs status`, ou un hook).
- **La tentation `version: main`** rejoue exactement le `--remote --merge` de 2026 : si les pins sont des branches, `make deps` déplace le code sous les pieds. La règle « `version:` est toujours un tag » doit être écrite et respectée.
- **Le partage vivant avec SUAS fonctionne** : les deux dépôts pointent le même `tools` ; une correction poussée dans `tools` est disponible pour les deux au prochain bump.
- **Le template** doit contenir un `deps.repos` qui pointe des dépôts existants, donc le template dépend de l'extérieur. Si `tools` change d'API, le template casse silencieusement.
- **Formation** : la recrue doit comprendre qu'il y a des dépôts dans le dépôt, même sans sous-modules. C'est une notion de plus en formation 5, et une source de questions Discord.

**Effort de mise en place** : environ 4 h (scinder les paquets partagés en dépôts propres, tagger, écrire `make deps`, `make status`, documenter la règle des tags). Effort récurrent : un bump de version par changement partagé.

---

## 3. Option C : sous-modules, mais peu, et corrigés

Le modèle 2026 gardé, avec les trois corrections de la revue : au plus trois sous-modules (`custom_interfaces`, `tools`, `nav_stack`), `ensure_submodules.sh` sans `--remote`, un seul workspace.

### Ce que fait un nouveau

| Action | Commandes |
|---|---|
| Jour 1 | `git clone --recurse-submodules` (ou `git submodule update --init` si oublié), `make build C=sim`. |
| Modifier `tools` | `cd packages/tools`, **sortir du detached HEAD** (`git switch main` ou une branche), commit, push, PR dans `tools`, puis `git add packages/tools` et commit dans aeac-2027 pour déplacer le pointeur. |
| Récupérer les changements d'un collègue | `git pull` puis `git submodule update`, sinon le pointeur local reste en arrière et `git status` affiche un `packages/tools (modified content)` incompréhensible. |

### Implications

- **Tout ce que la revue a documenté reste vrai** en plus petit : detached HEAD, pointeurs à déplacer, `git status` bruité, `.gitmodules` qui peut diverger du checkout. Réduire de 8 à 3 réduit la surface, pas la nature du piège.
- **Avantage réel** : c'est natif à git, rien à installer, GitHub affiche le lien vers le commit épinglé, et c'est ce que les directeurs actuels connaissent.
- **Partage vivant avec SUAS** : fonctionne, comme B.
- **Formation** : la revue a déjà tranché que les sous-modules sont un des trois seuls sujets git enseignés. Avec A ou B, ce sujet disparaît de la formation 5 ; avec C, il y reste et coûte une heure de contenu.

**Effort de mise en place** : environ 2 h (nettoyer les sous-modules existants, réécrire le script). Effort récurrent : chaque contribution à un paquet partagé demande le rituel du pointeur, et chaque cohorte redécouvre le detached HEAD.

---

## 4. Comparaison

| Critère | A. Monorepo | B. `.repos` | C. Sous-modules (3) |
|---|---|---|---|
| Étapes au clone | 1 | 2 | 1 si `--recurse-submodules`, sinon 2 et erreur cryptique |
| Ajouter un paquet de mission | `pkg create` + `exec_depend` | idem | idem |
| Modifier un paquet partagé | 1 commit, 1 PR | 2 commits, 2 PR, bump de tag | 2 commits, 2 PR, detached HEAD à gérer |
| `git status` voit tout | oui | non (partagés ignorés) | partiellement (bruit `modified content`) |
| Partage entre missions et machines (B1, B2) | `package.xml` | `package.xml` | `package.xml` |
| Partage inter-années (B3) | copie (A1) ou même dépôt (A2) | tag dans `deps.repos` | pointeur de commit |
| Partage vivant AEAC + SUAS 2027 | seulement en A2 (même dépôt) | oui | oui |
| Dérive silencieuse possible | non | si `version:` est une branche | si `--remote` revient |
| Le template dépend de dépôts externes | non | oui | oui |
| Notions git nouvelles en formation 5 | 0 | 1 (vcs import, pins) | 1 (sous-modules, plus lourde) |
| Outil à installer | rien | `vcstool` (dans l'image Docker) | rien |
| Mise en place | ~2 h | ~4 h | ~2 h |
| Coût récurrent | purge annuelle (A2) ou copie (A1) | un bump par changement partagé | rituel du pointeur |

---

## 5. Recommandation

**A, avec A2 (continuité du dépôt) pour la question de l'année, et B documenté en réserve.**

Pourquoi A : c'est la seule option où un nouveau n'a rien à apprendre au-delà de ce que la formation 3 enseigne déjà, où le template ne dépend de rien d'extérieur, et où la dérive silencieuse est impossible. Le seul cas que A ne couvre pas est le partage vivant entre deux dépôts en parallèle, et 2026 a montré que ce cas était théorique.

Pourquoi A2 plutôt que A1 : SUAS 2027 se prépare en même temps qu'AEAC 2027, avec la même équipe contrôle, la même infra réseau et le même `tools`. Deux dépôts, c'est deux copies de `tools` à garder synchronisées à la main pendant l'année la plus chargée. Un seul dépôt avec `C=aeac-recon`, `C=aeac-intervention`, `C=suas`, c'est zéro synchronisation. Le nom du dépôt devient un choix à faire : garder `aeac-2027` (déjà créé) et accepter qu'il contienne SUAS, ou le renommer `missions` dès maintenant. Une purge après chaque PODR (supprimer les bringup et paquets de mission morts, tagger avant) tient le dépôt propre ; c'est une tâche de lead, pas de recrue.

Pourquoi garder B en réserve et pas C : si un jour un paquet doit vraiment vivre dans deux dépôts (par exemple `tools` utilisé par le VTOL, qui a sa propre équipe et son propre rythme), `.repos` fait le travail avec un pin lisible et sans detached HEAD. La migration d'un paquet de A vers B est locale : déplacer le dossier dans son propre dépôt, ajouter une entrée dans `deps.repos`, et rien d'autre ne change puisque le workspace voit toujours le même chemin. Le plan d'architecture décrira cette migration en une demi-page « pour les leads ».

Si la recommandation est retenue, ce que le plan d'architecture aeac-2027 fixera :

1. Un seul workspace `ws/`, `ws/src` symlink vers `packages/`.
2. Une mission = un paquet `<mission>_bringup` (launch + `package.xml` qui liste ses dépendances) + un `config/<mission>.yaml` + une cible `make <mission>` qui fait `--packages-up-to`.
3. `packages/` à plat, aucun sous-module maison ; `zed-ros2-wrapper` reste un sous-module tiers hors du workspace.
4. Tag `<compétition>-<année>` posé le jour du départ en compétition, purge des paquets morts après le PODR.
5. Une demi-page « migrer un paquet vers un dépôt partagé avec `.repos` », pour les leads.

---

## 6. Discussion du 21 septembre 2026 : retour sur la recommandation

Commentaires de Colin sur la version ci-dessus : pas de recopie de code entre les années ; SUAS 2027 aura son propre dépôt ; le dépôt garde le nom `aeac-2027` ; `zed-ros2-wrapper` reste un sous-module ; préférence pour C, « mais on essaye de simplifier au max l'utilisation ».

Avec ces contraintes, l'option A n'a plus d'avantage : ses deux forces (un seul git, rien à synchroniser) reposaient sur l'absence de partage inter-dépôts, et le partage est justement l'objectif. Entre B et C, C est natif, connu des directeurs, affiché par GitHub, et n'a pas le `git status` aveugle de B. **Option retenue : C, dans la version simplifiée ci-dessous.**

### 6.1 Les cinq causes de la douleur 2026, et leur correction

| # | Cause en 2026 | Correction dans aeac-2027 |
|---|---|---|
| 1 | `ensure_submodules.sh` faisait `--remote --merge` : les pointeurs bougeaient à chaque exécution | `make init` fait uniquement `git submodule update --init`. Déplacer un pointeur est un geste volontaire : `make bump PKG=tools` (pull de `main` dans le sous-module, `git add packages/tools`), réservé aux leads. |
| 2 | Après un `git pull`, les sous-modules restaient en arrière ; `git status` affichait un `modified content` incompris | `make init` pose deux réglages git locaux : `submodule.recurse=true` (un `git pull` ou `git switch` met les sous-modules au bon commit tout seul) et `push.recurseSubmodules=on-demand` (git refuse de pousser un pointeur vers un commit qui n'est pas lui-même poussé). |
| 3 | Nesting `packages/nav_stack/nav_stack/nav_stack/init.py` | Règle : un dépôt partagé = un paquet ROS, `package.xml` à la racine du dépôt. On retombe à `packages/nav_stack/nav_stack/init.py`, deux niveaux comme tout paquet Python ROS. À appliquer au moment de créer les dépôts 2027 (les dépôts 2026 gardent leur forme). |
| 4 | Detached HEAD dans le sous-module quand on veut y coder | Les recrues codent dans `packages/` local (paquets de mission, suivis directement par aeac-2027) et ne touchent pas aux sous-modules. Un seul signal enseigné : si `git status` affiche `packages/tools (new commits)` ou `(modified content)`, tu as modifié un dépôt partagé, demande à un lead. Le geste complet (`git -C packages/tools switch main`, commit, push, puis pointeur) est documenté dans `ARCHITECTURE.md` en section « pour les leads ». |
| 5 | Huit sous-modules, dont un vide et un jamais utilisé | Trois maison dans le template : `custom_interfaces`, `tools`, `nav_stack`. Plus `zed-ros2-wrapper` en tiers, hors du workspace, marqué « ne pas modifier ». Un paquet de mission ne devient sous-module que lorsqu'un deuxième dépôt le demande, et c'est une décision de lead. |

Ce qui ne change pas par rapport aux sections 1 à 3 : un seul workspace, `ws/src` vers `packages/`, la mission choisit ses paquets par `package.xml` et `colcon build --packages-up-to <mission>_bringup`. Plus de `pkgs.txt`, plus de `link_ws.sh`, plus de bind-mounts un par un.

### 6.2 Ce que la recrue voit

| Action | Commandes |
|---|---|
| Jour 1 | `git clone --recurse-submodules` (le README le dit ; si oublié, `make init` rattrape et `make build` refuse de partir tant que `packages/tools` est vide, avec un message clair). |
| Ajouter un paquet de mission | `ros2 pkg create` dans `packages/`, `<exec_depend>` dans le bringup de sa mission. |
| Coder dans un paquet de mission | Un seul git, branche, commit, PR. Rien de nouveau par rapport à la formation 0. |
| Récupérer le travail des autres | `git pull`. Les sous-modules suivent grâce à `submodule.recurse`. |
| Toucher à `tools` | Pas en formation. Signal dans `git status`, puis un lead. |

### 6.3 Ce que le lead voit

- `make bump PKG=<nom>` : avance le sous-module sur `origin/main`, stage le pointeur, affiche le diff de commits. Un commit `bump <nom> to <sha>` suit.
- Contribuer à un paquet partagé : `git -C packages/<nom> switch main`, coder, commit, push, PR dans le dépôt du paquet, puis `make bump`.
- Créer un nouveau paquet partagé : nouveau dépôt GitHub avec `package.xml` à la racine, `git submodule add` dans `packages/`, une ligne dans `ARCHITECTURE.md`.
- Sortir un paquet du partage (il ne sert plus qu'ici) : `git submodule deinit`, copier le dossier, `git rm`, `git add`. Une commande par ligne dans `ARCHITECTURE.md`.

### 6.4 Ce que le plan d'architecture fixera

1. Un seul workspace `ws/`, `ws/src` symlink vers `packages/`.
2. Une mission = `packages/<mission>_bringup` (launch, `package.xml` qui liste ses dépendances) + `config/<mission>.yaml` + cible `make <mission>` qui fait `--packages-up-to`.
3. Quatre sous-modules dans le template : `custom_interfaces`, `tools`, `nav_stack`, `zed-ros2-wrapper`. Un paquet ROS par dépôt partagé, `package.xml` à la racine.
4. `make init` idempotent (`submodule update --init` + les deux réglages git) ; `make bump PKG=` pour les leads ; aucun script qui fait `--remote`.
5. Un paragraphe « sous-modules en trois phrases » dans `ARCHITECTURE.md` pour les recrues, et une section « pour les leads » avec les gestes de 6.3.

### 6.5 B contre C, geste par geste

Demande de Colin : « je vais y aller vers B ou C, compare étroitement les deux ». Les deux options ont un seul workspace et `package.xml` comme mécanisme de mission ; seul le pointeur vers les paquets partagés diffère. Hypothèses : C est la version simplifiée de 6.1 (`make init`, deux réglages git, `make bump`) ; B est `deps.repos` avec `version:` toujours un tag, `packages/shared/` dans `.gitignore`, `make deps`.

| Geste | B. `deps.repos` (vcstool) | C. Sous-modules simplifiés | Avantage |
|---|---|---|---|
| **Clone** | `git clone` puis `make deps`. Toujours deux étapes. | `git clone --recurse-submodules`, une étape ; si oublié, `make init` rattrape. | C, légèrement |
| **Oubli de l'étape d'import** | `packages/shared/` absent, `colcon` échoue sur une dépendance manquante : message ROS peu parlant. | `packages/tools/` vide, `make build` refuse avec un message maison. Même garde-fou possible en B. | Égalité si les deux Makefile vérifient |
| **Voir ce qui est épinglé** | Ouvrir `deps.repos` : un tag lisible (`v2027.1`). | `git submodule status` : un SHA. GitHub affiche le lien vers le commit. | B |
| **`git pull` après qu'un lead a avancé un paquet partagé** | Rien ne bouge dans `packages/shared/` tant qu'on ne relance pas `make deps`. Aucun signal que `deps.repos` a changé. On construit sur une vieille version sans le savoir. | Avec `submodule.recurse=true`, le sous-module suit le pull. Sans le réglage, `git status` affiche `(new commits)` : un signal, même cryptique. | **C, nettement** (dérive silencieuse en B) |
| **Éditer un paquet partagé** | Le paquet est en detached HEAD sur le tag. Il faut `git switch main` avant de coder, comme en C. | Detached HEAD sur le commit épinglé. `git switch main` avant de coder. | Égalité (B n'élimine pas le detached HEAD) |
| **Une recrue modifie `tools` sans le savoir** | Invisible : `git status` à la racine ne montre rien, `git commit -a` ne prend rien, le travail reste local et peut être perdu. | Visible : `git status` affiche `packages/tools (modified content)`. C'est le signal enseigné « demande à un lead ». | **C, nettement** |
| **Pousser une avancée de paquet partagé** | Commit + push dans le paquet, créer un tag, éditer `deps.repos`, commit, push. Rien ne vérifie que le tag existe sur GitHub. | Commit + push dans le paquet, `make bump`, commit, push. `push.recurseSubmodules=on-demand` refuse de pousser un pointeur vers un commit non poussé. | C (garde-fou natif) |
| **Avancer un paquet partagé (lead)** | Poser un tag dans le paquet (ou copier un SHA), éditer le YAML. Discipline de tags à tenir. | `make bump PKG=tools` : pull de `main`, `git add`, diff des commits affiché. | C, légèrement |
| **Revue de PR sur GitHub** | Diff lisible d'une ligne de YAML. | Diff `Subproject commit abc… → def…`, un clic pour voir les commits. | B, légèrement |
| **Outillage** | `vcstool` à installer sur l'hôte WSL et dans l'image Docker. | git seul. | C |
| **Build sur l'hôte hors conteneur** | Fonctionne après `make deps`. | Fonctionne après `make init`. | Égalité |
| **Partage entre aeac-2027, SUAS, VTOL** | Chaque dépôt pointe le même paquet à son tag. | Chaque dépôt pointe le même paquet à son commit. | Égalité |
| **Ce que connaissent déjà les directeurs** | Nouveau pour l'équipe. | Utilisé depuis 2025. | C |
| **Notions à enseigner en formation 5** | « Après un pull, fais `make deps` » ; « ce qui est dans `packages/shared/` n'est pas dans ce git ». | « Clone avec `--recurse-submodules` » ; « si `git status` parle d'un sous-module, demande à un lead ». | Égalité en volume ; les erreurs de C sont visibles, celles de B ne le sont pas |

**Lecture d'ensemble.** B gagne sur la lisibilité du pin et la propreté des PR. C gagne sur tout ce qui protège une recrue : un `pull` qui met à jour tout seul, un `status` qui montre les modifications partagées, un `push` qui refuse d'oublier un commit. Les modes de défaillance de B sont silencieux (construire sur une vieille version, perdre du travail non suivi) ; ceux de C sont bruyants (dossier vide, message `(new commits)`), et le bruit est ce qu'on veut pour des nouveaux. Le seul reproche sérieux à C, la dérive des pointeurs, venait du script `--remote`, pas du mécanisme.

**Recommandation finale : C simplifié.** Pour récupérer l'avantage de lisibilité de B sans en payer le prix, `make bump` pose aussi un tag `aeac-2027-<date>` dans le paquet partagé et `ARCHITECTURE.md` liste les paquets partagés avec leur rôle ; `make status` affiche `git submodule status` en une ligne par paquet.

### 6.6 Décisions (21 septembre 2026)

- **C simplifié** retenu tel que décrit en 6.1 à 6.5.
- Les trois dépôts partagés (`custom_interfaces`, `tools`, `nav_stack`) sont **repris et restructurés sur `main`** : historique gardé, un commit déplace `package.xml` à la racine et retire le code mort listé dans la revue.
- `vision` est finalement un **quatrième sous-module maison** dès le départ (décision revue le même jour) : il sera rendu plus versatile pour resservir d'une année à l'autre. Il est dans le template mais aucune mission du template n'en dépend, donc il n'est construit que sur le drone et seulement quand un bringup le demande.
- Suite : `PLAN-ARCHITECTURE-aeac-2027.md`, dans ce dossier.
