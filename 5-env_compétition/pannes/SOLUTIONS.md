# SOLUTIONS.md : pour les leads, pas pour les recrues

Correspondance patch / étage. L'ordre des numéros ne suit pas l'ordre des étages.

| Patch | Étage | Fichier touché |
|---|---|---|
| `panne-1.patch` | 2, nœud | `compose/sim.yml`, service `mavros-sim` |
| `panne-2.patch` | 1, conteneur | `compose/sim.yml`, service `sim` |
| `panne-3.patch` | 3, donnée | `config/demo.yaml` |

## panne-1 : le domaine ROS de mavros

**Ligne du patch** : `-      - ROS_DOMAIN_ID=3` / `+      - ROS_DOMAIN_ID=4` dans le bloc
`environment` du service `mavros-sim` de `compose/sim.yml`.

**Cause** : deux domaines DDS différents. Le conteneur `mavros-sim` publie dans le domaine 4,
le conteneur `sim` écoute le domaine 3. Deux domaines ne se voient pas, même sur la même machine
et même en `network_mode: host`.

**Ce que la recrue voit** : les deux conteneurs tournent (`docker ps` en montre deux), le nœud
`demo_mission` tourne et publie son état, mais le GO ne passe jamais et le nœud reste en `IDLE`
sans jamais rien recevoir. C'est l'étage nœud : tout tourne, rien ne se parle. Le premier
symptôme arrive avant le GO : `takeoff_test` échoue aussi, puisque mavros est sur le domaine 4
et le conteneur `sim` sur le 3.

**La commande qui la révèle** :

```bash
make shell C=demo IMG=sim
ros2 node list      # /demo_mission seul, aucun /mavros
ros2 topic list     # aucun /mavros/*, alors que mavros tourne
```

Puis, en sortant du conteneur :

```bash
docker compose -f compose/sim.yml exec mavros-sim env | grep ROS_DOMAIN
# ROS_DOMAIN_ID=4   alors que le conteneur sim répond 3
```

**La leçon** : `ros2 topic list` ne liste que ce qui partage le domaine et le RMW. Un topic
absent n'est pas la preuve qu'un nœud est mort ; c'est d'abord la preuve qu'on ne l'entend pas.
Les deux variables à comparer avant tout le reste sont `ROS_DOMAIN_ID` et `RMW_IMPLEMENTATION`.

## panne-2 : le dossier de travail du conteneur

**Ligne du patch** : `-    working_dir: /aeac/workspaces/${C:-gcs}_ws` /
`+    working_dir: /aeac/workspaces/${C:-gcs}_wss` dans le service `sim` de `compose/sim.yml`.

**Cause** : `_wss` avec un `s` de trop. Docker ne se plaint pas d'un `working_dir` absent, il
le crée (et comme le dépôt est monté, il le crée sur le poste : un dossier vide
`workspaces/demo_wss` apparaît). Le conteneur démarre donc dans un dossier vide, où
`source install/setup.bash` échoue ; `bash -lc` rend un code non nul et le conteneur sort
aussitôt.

**Ce que la recrue voit** : `make sim C=demo` rend la main tout de suite (avec
`--abort-on-container-exit`, la sortie de `sim` arrête aussi `mavros-sim`). Aucun nœud, aucun
topic, rien à déboguer côté ROS. C'est l'étage conteneur.

**La commande qui la révèle** :

```bash
docker ps                                  # aucun aeac-sim
docker ps -a                               # aeac-sim en Exited/Created
docker compose -f compose/sim.yml logs     # ou : make logs IMG=sim
# sim  | bash: line 1: install/setup.bash: No such file or directory
```

Le message ne nomme pas le vrai coupable : il dit qu'un fichier manque, pas que le dossier de
travail est le mauvais. C'est `docker inspect aeac-sim --format '{{.Config.WorkingDir}}'`, ou
la lecture de `compose/sim.yml`, qui finit de le dire. Penser à supprimer le dossier vide
`workspaces/demo_wss` laissé par Docker après avoir retiré la panne.

**La leçon** : quand rien ne répond, on ne lance pas `ros2 topic list`, on regarde d'abord si
le conteneur est vivant. `docker ps -a` et les logs du conteneur disent en une ligne ce qu'une
demi-heure de `ros2 node list` ne dira jamais. À noter aussi : le chemin est celui vu dans le
conteneur (`/aeac/...`), pas celui du poste.

## panne-3 : le canal du GO

**Ligne du patch** : `-      go_channel: 7` / `+      go_channel: 12` dans
`config/demo.yaml`, sous `demo_mission: ros__parameters: rc:`.

**Cause** : le nœud lit le GO sur l'index 12 de `RCIn.channels` alors que le `rc_simulator`
l'envoie sur l'index 7 (le canal 8 de la manette). Le code fait exactement ce qu'on lui demande,
c'est la valeur qu'on lui demande qui est fausse.

**Ce que la recrue voit** : tout tourne, les deux conteneurs, mavros, le nœud, les topics
`/mavros/*` sont là. La touche `w` du `rc_simulator` ne change rien : l'état reste `IDLE` pour
toujours et aucun avertissement ne sort. C'est l'étage donnée.

**La commande qui la révèle** :

```bash
ros2 topic echo /mavros/rc/in
# channels: [1500, ..., 1900, ...]   la 8e valeur (index 7) bouge quand on appuie sur w
ros2 param get /demo_mission rc.go_channel
# Integer value is: 12               le nœud regarde ailleurs
```

Selon la longueur du tableau `channels` publié par le SITL, l'index 12 peut aussi ne pas exister
du tout : `mission.py` teste `self.go_channel < len(msg.channels)` et ne lève donc rien.

**La leçon** : un paramètre est une donnée, et une donnée se vérifie sur le nœud vivant
(`ros2 param get`), pas dans le fichier YAML du dépôt. Le fichier lu est celui de `config/` du
clone, copié à `/aeac/config/demo.yaml` dans le conteneur ; le YAML de `workspaces/demo_ws/`
n'est qu'un exemple à copier, le modifier ne change rien à ce qui tourne. C'est le piège
préféré de cette panne.

## Conduite de l'exercice

Appliquer une panne à la fois, retirer avec `git apply -R`, laisser chercher. Si la recrue saute
un étage, ne pas donner la réponse : demander « comment sais-tu que le conteneur tourne ? »,
puis « comment sais-tu que le nœud reçoit ? ». Les trois pannes ensemble prennent environ une
heure ; la panne 2 est la plus rapide, la panne 3 la plus longue.
