# Plan de la formation 6 : réseau, Zenoh, services et capteurs

*Document de travail, 21 septembre 2026. Ce n'est pas la formation : c'est sa structure, le contenu à y mettre et les questions à trancher avant la rédaction. Sources : le plan d'apprentissage (bloc B6 « Réseau et environnement de compétition », objectif 5, jalon du 21 novembre), le squelette `mission-template/` (`ARCHITECTURE.md`, `config/`, `systemd/`, `compose/zed.yml`), la branche de compétition d'aeac-2026 et la revue pédagogique (sections 3.2 et 4).*

*C'est la suite directe de la formation 5, qui a nommé ces sujets en une phrase chacun. Ici on les ouvre. Ce qui reste hors périmètre : la préparation matérielle de la Jetson (JetPack, UART, `dialout`, adresse statique), qui est le bloc B7 ; la vision et les modèles, bloc B8.*

---

## 0. Ce que la formation doit accomplir

### Le public

Un membre qui a fait la formation 5 : il a fait tourner la démo en simulation et ajouté un nœud. Il sait qu'un topic `external` traverse la radio et que systemd est un emballage, mais il ne sait pas comment ni pourquoi. Il se prépare à la compétition : il sera un jour au bord du terrain, le sol ne voit rien, et il doit trouver en cinq minutes si c'est la radio, Zenoh, un domaine ou un service qui n'est pas parti. Il n'a pas nécessairement de Jetson sous la main pendant la formation.

C'est aussi le savoir le moins externalisable de l'équipe, celui qui part avec les directeurs en avril. La formation sert à le fixer.

### Le résultat attendu

À la fin, le membre est capable de :

- Dessiner le réseau du drone avec ses deux liens (SIYI HM30, LTE plus Tailscale), les adresses, et dire dans quel ordre on vérifie quand rien ne passe.
- Expliquer pourquoi le drone et le sol sont sur deux domaines ROS différents et pourquoi DDS ne sort jamais d'une machine.
- Lire les deux fichiers Zenoh (air et sol), dire ce que chaque bloc fait, et rendre un topic visible côté sol en le nommant.
- Lire une unité systemd du dépôt, prédire l'ordre de démarrage, et retrouver dans `journalctl` pourquoi un service n'est pas parti.
- Décrire, avec la ZED comme exemple, les six décisions à prendre pour intégrer un capteur qui a son propre pilote, et remplir la fiche pour un capteur nouveau.

### Le fil conducteur

**Le chemin d'un topic, du capteur au portable.** Une détection naît dans le conteneur vision à partir d'une image de la ZED, devient un topic `internal` sur le domaine 2, est consommée par la mission, qui publie un résumé `external` ; le pont Zenoh de l'air le prend, il traverse la SIYI (ou Tailscale), le pont du sol le dépose sur le domaine 3, et le portable l'affiche. Chaque document suit un tronçon de ce chemin, en remontant depuis le portable : d'abord le lien radio et les adresses (6.1), puis le pont (6.2), puis ce qui a lancé tout ça au boot (6.3), puis le capteur à l'origine (6.4).

Sans Jetson, le chemin se reproduit sur le poste : deux conteneurs sur deux domaines, un pont Zenoh entre les deux, sur la même machine. C'est l'exercice central de 6.2 et il ne demande aucun matériel.

### Ce qui distingue cette formation des autres

Elle porte sur du matériel que la plupart des membres n'ont pas. Trois parades :

- **Tout ce qui peut se reproduire sur le poste s'y reproduit** : le pont Zenoh entre deux domaines, la lecture des unités systemd et, si WSL le permet, une unité factice (question 3).
- **Ce qui demande la Jetson est une séance avec un lead**, une fois, en groupe, sur le drone à l'atelier. Les jalons correspondants sont marqués « séance ».
- **Chaque section donne une procédure de diagnostic ordonnée**, pas seulement une explication. Le document 6.1 se termine sur la table de `procédure.md` (« le sol ne voit rien ») réécrite avec le pourquoi de chaque étape.

---

## 1. Découpage proposé

| Document | Sujet | Réussite | Durée estimée |
|---|---|---|---|
| 6.1 Le réseau du drone | SIYI HM30, plan d'adressage, LTE et Tailscale, SSH, domaines ROS, `ROS_LOCALHOST_ONLY`, `lo-multicast` | Le schéma réseau dessiné de mémoire ; la table de diagnostic remplie avec le pourquoi | 1 h 30 |
| 6.2 Zenoh, le pont | Routeur et client, `allow`, découverte désactivée, un fichier par drone, diagnostic | Un topic `external` publié sur le domaine 2 lu sur le domaine 3 à travers un pont local ; un topic `internal` qui ne passe pas | 2 h |
| 6.3 Les services au boot | Anatomie d'une unité, ordre, attente du périphérique, `Restart`, `make deploy`, `journalctl`, retour à la main | L'ordre de démarrage prédit puis vérifié ; une panne trouvée dans `journalctl` (séance ou unité factice) | 1 h 30 |
| 6.4 Intégrer un capteur : la ZED | Pilote du fabricant, wrapper tiers en sous-module, image à part, compose, paramètres, unité, topics | La fiche d'intégration remplie pour la ZED, puis pour un second capteur | 2 h |

Total : environ 7 h pour le membre, plus une séance d'atelier de deux heures. Rédaction : environ 10 h ; voir la question 1.

---

## 2. Document 6.1 : le réseau du drone

### Objectifs

- Nommer les deux liens entre le drone et le sol et savoir lequel est actif.
- Retrouver l'adresse d'un drone et s'y connecter.
- Expliquer les domaines 2 et 3, `ROS_LOCALHOST_ONLY=1` et le service `lo-multicast`.
- Diagnostiquer « le sol ne voit rien » dans l'ordre, en sachant pourquoi cet ordre.

### Bloc « Avant de commencer »

- Durée : 1 h 30.
- Prérequis : formation 5. Formation 0 pour `ping`, adresse IP, port, SSH.
- À la fin : le schéma réseau dessiné et la table de diagnostic complétée.
- À poster à la fin : le schéma et la table.

### 1. Deux liens, un plan d'adressage

- La SIYI HM30 : un pont Ethernet par radio. La Jetson et le portable sont sur le même réseau `192.168.144.x` comme s'ils étaient reliés par un câble. Ce que la radio transporte : vidéo, MAVLink vers Mission Planner, et le trafic Zenoh. Ce qu'elle ne fait pas : du routage. Portée, ce qui la coupe (obstacle, antenne mal orientée).
- Le secours : une clé LTE sur la Jetson et Tailscale des deux côtés. Chaque machine a une seconde adresse `100.x.y.z` qui marche partout où il y a du réseau cellulaire. Plus lent, plus de latence, mais ça passe quand la SIYI est perdue.
- Le tableau d'`ARCHITECTURE.md` : Hexa `192.168.144.30` et `100.87.171.82`, OS `192.168.144.31` et `100.64.95.10`. Règle : un nouveau drone est une ligne de plus et un fichier de plus dans `config/drones/`.
- SSH : `ssh zenith@<adresse>`, et c'est tout ce qu'on en dit ici. Le reste (clés, adresse statique, mDNS) est le bloc B7.

Exercice : dessiner les deux machines, les deux liens, les quatre adresses. Puis, avec un lead ou avec les adresses fournies, `ping` sur les deux adresses d'un drone allumé et noter laquelle répond.

### 2. Deux domaines et DDS enfermé

Trois phrases d'`ARCHITECTURE.md` développées en une page :

- **Le nom du topic dit où il voyage.** Rappel de la formation 5, avec cette fois la raison : c'est la liste `allow` du pont (6.2) qui lit le nom.
- **DDS ne sort jamais d'une machine.** `ROS_LOCALHOST_ONLY=1` dans tous les compose qui touchent à Zenoh. Pourquoi : la découverte DDS multicast sur une radio est lente, bavarde et imprévisible ; on la coupe et on laisse Zenoh porter ce qu'il faut. Conséquence sur la Jetson : le multicast sur l'interface `lo` doit être activé, d'où `lo-multicast.service`, la première unité au boot. Symptôme quand il manque : `ros2 topic list` vide entre deux conteneurs de la même Jetson.
- **Deux domaines différents.** 2 sur le drone, 3 au sol. Un DDS mal configuré ne traverse jamais la radio par accident, et un portable qui oublie `ROS_LOCALHOST_ONLY` ne voit pas le drone d'un autre. Le pont, lui, sait qu'il relie 2 et 3.

Exercice sur le poste : dans `make dev`, ouvrir deux shells, changer `ROS_DOMAIN_ID` dans l'un, constater que `ros2 topic list` ne voit plus rien. Revenir.

### 3. Diagnostiquer dans l'ordre

La table de `procédure.md` (« le sol ne voit rien »), réécrite avec une colonne « ce que ça teste » :

| Étape | Commande | Ce que ça teste | Si ça échoue |
|---|---|---|---|
| 1 | `ping 192.168.144.30` | Le lien SIYI | Antennes, alimentation de la radio, câble Ethernet côté portable |
| 2 | `ping 100.87.171.82` | Le secours Tailscale | Clé LTE, Tailscale démarré des deux côtés |
| 3 | `docker logs aeac-zenoh-ground` | Le pont du sol trouve-t-il le routeur du drone ? | Le `DRONE=` passé à `make gcs`, le port 7447, 6.2 |
| 4 | `ssh` puis `make zenoh-air-status` | Le pont de l'air tourne-t-il ? | `make zenoh-air-logs`, 6.3 |
| 5 | `ssh` puis `make shell IMG=drone`, `ros2 topic list` | La mission publie-t-elle ? | `make mission-logs` |
| 6 | Le nom du topic | Est-il `external` ? | Formation 5, section 5.3 |

Jalon : la table remplie de mémoire, puis comparée.

### Quand ça casse (6.1)

| Symptôme | Cause probable | Remède |
|---|---|---|
| `ping` SIYI passe, Tailscale non | Tailscale pas démarré ou pas connecté sur la Jetson | `tailscale status` des deux côtés |
| Les deux `ping` échouent | Jetson éteinte ou pas démarrée | Attendre une minute après le boot ; écran ou série |
| `ros2 topic list` vide entre deux conteneurs de la Jetson | `lo-multicast` pas actif | `make lo-multicast-status` |
| Le portable voit les topics d'un autre drone | `DRONE=` faux | `make print-vars` |

---

## 3. Document 6.2 : Zenoh, le pont

### Objectifs

- Lire `config/zenoh-air.json5` et `config/drones/<drone>.json5` bloc par bloc.
- Expliquer routeur et client, la découverte désactivée, les listes `allow`, les deux endpoints.
- Faire passer un topic entre deux domaines sur le poste, sans matériel.
- Diagnostiquer un pont qui ne relie pas.

### Bloc « Avant de commencer »

- Durée : 2 h.
- Prérequis : 6.1.
- À la fin : un pont Zenoh local relie deux conteneurs sur les domaines 2 et 3 ; un topic `external` passe, un topic `internal` ne passe pas.
- À poster à la fin : les deux `ros2 topic list`, côté 2 et côté 3, côte à côte.

### 1. Ce que Zenoh fait, en une image

Le pont `zenoh-bridge-ros2dds` est un nœud qui s'abonne côté DDS à ce que sa liste `allow` autorise et le republie côté Zenoh, et l'inverse. Deux ponts, un par machine, se parlent en TCP sur le port 7447. Ce n'est pas un RMW, ROS ne sait pas qu'il existe : les nœuds voient des topics ordinaires. C'est pour ça que la formation 5 pouvait dire « le préfixe suffit ».

### 2. Les deux fichiers, bloc par bloc

`zenoh-air.json5`, côté drone :

- `plugins.ros2dds.domain: 2` et `ros_localhost_only: true` : le pont regarde le DDS local du domaine 2, rien d'autre.
- `allow.publishers` et `allow.subscribers` : `/tf`, `/tf_static`, `/aeac/external.*`. C'est la ligne qui donne son sens au nom du topic. Ce qui n'est pas là ne passe pas, même si un nœud le publie.
- `mode: "router"`, `listen: tcp/0.0.0.0:7447` : le drone attend, le sol vient.
- `scouting.multicast` et `gossip` désactivés : pas de découverte automatique. Pourquoi : deux drones ou deux portables sur le même réseau ne doivent pas se trouver par surprise. Le prix : il faut écrire l'adresse du drone quelque part, et ce quelque part est le fichier par drone.

`drones/hexa.json5`, côté sol :

- `domain: 3`, mêmes listes `allow`.
- `mode: "client"`, `connect.endpoints` : la SIYI et Tailscale, dans cet ordre, avec `retry` : le pont essaie les deux, indéfiniment. Le lien de secours est dans la config, pas dans la tête de quelqu'un.
- `exit_on_failure: false` : le conteneur ne meurt pas quand le drone n'est pas encore là.

Exercice de lecture : `hexa.json5` et `os.json5` côte à côte, `diff`. Deux lignes diffèrent. Puis ajouter un troisième drone fictif.

### 3. Le pont sur le poste

L'exercice central, sans matériel. Un fichier compose fourni par la formation (question 2) lance sur le poste : un conteneur `air` (domaine 2, `ROS_LOCALHOST_ONLY=1`) avec `zenoh-air.json5`, un conteneur `ground` (domaine 3) avec un `config/drones/local.json5` dont l'endpoint est `tcp/127.0.0.1:7447`, et deux shells.

Déroulé :

1. Dans `air` : `ros2 topic pub /aeac/external/demo/hello std_msgs/String "{data: salut}"`.
2. Dans `ground` : `ros2 topic list`, le topic est là ; `ros2 topic echo`, le message arrive.
3. Dans `air` : `ros2 topic pub /aeac/internal/demo/secret ...`. Dans `ground` : il n'apparaît pas.
4. Dans `air` : arrêter le pont (`docker compose stop zenoh-air`). Dans `ground` : `docker logs` du pont du sol, voir le `retry`. Relancer, voir la reconnexion.
5. Modifier `allow` pour laisser passer `/aeac/internal/demo/secret`, relancer, constater, remettre. Conclusion : on ne touche pas à `allow`, on nomme le topic.

Jalon : les deux `ros2 topic list`.

### 4. Diagnostiquer un pont

Dans l'ordre : le pont du sol tourne-t-il (`docker ps`) ; ses logs disent-ils `connected` ou `retry` ; le pont de l'air tourne-t-il (`make zenoh-air-status`) ; le topic est-il dans `allow` ; le nœud publie-t-il vraiment côté drone. Ce qui n'existe pas et qu'on ne cherche pas : un outil graphique Zenoh. Les logs suffisent.

### Quand ça casse (6.2)

| Symptôme | Cause probable | Remède |
|---|---|---|
| Le pont du sol boucle sur `retry` | Mauvaise adresse, port 7447 fermé, pont de l'air arrêté | 6.1 étapes 1 à 4 |
| Le topic est dans `ros2 topic list` côté sol mais `echo` reste muet | QoS incompatible, ou `reliable_routes_blocking` | `ros2 topic info -v` des deux côtés |
| `/tf` passe mais pas le topic de mission | Nom sans le préfixe `external` | Formation 5, section 5.3 |
| Deux portables voient le même drone | Voulu ; le routeur accepte plusieurs clients | Rien, mais un seul pilote |

---

## 4. Document 6.3 : les services au boot

### Objectifs

- Lire une unité systemd du dépôt et dire ce que fait chaque ligne.
- Prédire l'ordre de démarrage à partir des `After` et le vérifier.
- Expliquer `make deploy` et `make undeploy`, et savoir quand on déploie.
- Trouver dans `journalctl` pourquoi un service n'est pas parti.

### Bloc « Avant de commencer »

- Durée : 1 h 30, plus la séance d'atelier pour les jalons marqués « séance ».
- Prérequis : formation 5 (la phrase « systemd est un emballage »), 6.1.
- À la fin : les six unités lues, l'ordre prédit, une panne diagnostiquée.
- À poster à la fin : l'ordre de démarrage prédit et la ligne de `journalctl` qui explique la panne.

### 1. Pourquoi systemd, et pourquoi seulement sur la Jetson

Le drone doit démarrer seul : personne ne tape `make mavros` au bord du terrain. systemd lance au boot exactement ce que les cibles `make` de la section 2 lancent à la main, relance ce qui tombe, et garde les logs. Sur le poste WSL il n'est pas nécessaire et le Makefile ne le suppose jamais. La règle du dépôt : toute unité a une cible `make` équivalente, et pour tester on fait `make undeploy` puis les cibles à la main.

### 2. Anatomie d'une unité, sur `mavros.service`

Ligne par ligne : `[Unit]` (`Description`, `After`, `Wants`, `Requires`), `[Service]` (`WorkingDirectory=__REPO__`, `ExecStartPre` qui attend `/dev/ttyTHS1`, `ExecStart` qui est un `docker compose up` en avant-plan pour que `journalctl` voie les logs, `ExecStop`, `Restart=always`, `RestartSec`), `[Install]` (`WantedBy=multi-user.target`). Le `__REPO__` : remplacé par `make deploy` avec le chemin du dépôt, pour qu'un dépôt cloné ailleurs marche.

Puis les cinq autres, en diff par rapport à `mavros.service` : `zed` attend `lsusb`, `mission` lit `/etc/aeac/mission`, `lo-multicast` est un `oneshot`, `vision` vient après `zed`.

### 3. L'ordre au boot

Exercice : à partir des seuls `After` des six fichiers, dessiner le graphe et écrire l'ordre. Réponse : `lo-multicast`, `mavros`, `zed`, `zenoh-air`, `vision`, `mission`. Puis ce qu'`After` ne garantit pas : que le service précédent est *prêt*, seulement qu'il est *lancé*. C'est pour ça que `ExecStartPre` attend le périphérique et que `Restart=always` rattrape un départ trop tôt. Jalon : l'ordre.

Séance : sur la Jetson, `systemctl list-dependencies mission.service`, puis `journalctl -b -u mavros -u mission` pour voir l'ordre réel avec les horodatages.

### 4. `make deploy`, `make undeploy`, changer de mission

Lecture de la cible `deploy` : `sed` du `__REPO__`, `/etc/aeac/mission`, `daemon-reload`, `enable --now`. Ce qu'elle ne fait pas : construire les images. Changer de mission : `make deploy C=<autre>`. Repasser à la main : `make undeploy`, puis `make mavros` et `make drone C=` dans deux terminaux.

Séance : déployer, redémarrer la Jetson, `make mission-status` après une minute.

### 5. Trouver une panne

Trois cas à reconnaître dans `journalctl -u <service>` : le `ExecStartPre` qui boucle (le périphérique n'est jamais apparu : câble, port, JetPack 5 contre 6), le compose qui échoue (image absente, fichier de config manquant), le service qui redémarre en boucle (`Restart=always` masque une erreur dans le nœud ; lire les logs du conteneur). Les cibles : `make <service>-status`, `make <service>-logs`, `make <service>-restart`.

Exercice sans matériel (question 3) : si WSL a systemd, une unité `formation.service` fournie qui attend un fichier dans `ExecStartPre` ; le membre la démarre, voit qu'elle boucle dans `journalctl`, crée le fichier, voit qu'elle part. Sinon : trois extraits de `journalctl` réels fournis, à diagnostiquer sur papier.

### Quand ça casse (6.3)

| Symptôme | Cause probable | Remède |
|---|---|---|
| `mavros` en `activating` sans fin | `/dev/ttyTHS1` absent | Câble, ou `ttyTHS0` sur JetPack 5 (B7) |
| `mission` en boucle de redémarrage | Le launch plante | `make mission-logs`, puis `make undeploy` et `make drone C=` pour voir l'erreur en clair |
| `make deploy` a marché mais rien ne part au boot | `enable` sans `daemon-reload`, ou `WorkingDirectory` faux | `systemctl cat mission.service`, vérifier le chemin |
| Deux missions se battent | Ancien `mission.service` d'un autre dépôt encore actif | `systemctl list-units | grep aeac`, `make undeploy` dans l'autre dépôt |

---

## 5. Document 6.4 : intégrer un capteur spécialisé, la ZED comme exemple

### Objectifs

- Distinguer un capteur qui parle MAVLink (l'autopilote s'en charge) d'un capteur qui a son propre pilote et son propre wrapper ROS 2.
- Suivre l'intégration de la ZED à travers les six décisions : pilote, wrapper, image, compose, paramètres, service.
- Savoir ce que l'équipe a modifié dans le wrapper et pourquoi c'est un sous-module tiers sur une branche `zenith`.
- Remplir la fiche d'intégration pour un capteur nouveau.

### Bloc « Avant de commencer »

- Durée : 2 h.
- Prérequis : 6.1 à 6.3, formation 5.
- À la fin : la fiche d'intégration remplie pour la ZED (corrigée), puis pour un second capteur (à faire relire).
- À poster à la fin : la seconde fiche.

### 1. Deux familles de capteurs

Le GPS, le baromètre, la boussole : branchés sur le Pixhawk, l'autopilote les lit, mavros les republie. On ne fait rien. La ZED, un lidar, une caméra thermique : branchés sur la Jetson, avec un pilote du fabricant et souvent un wrapper ROS 2 du fabricant. Là il y a six décisions à prendre, et la ZED sert d'exemple pour chacune.

### 2. Les six décisions, sur la ZED

1. **Le pilote.** Le SDK ZED s'installe sur la Jetson elle-même (JetPack, CUDA), pas dans nos images. Les dossiers `/usr/local/zed/resources` et `settings` sont montés dans le conteneur. Pourquoi : le SDK est lourd, lié à la version de JetPack, et il calibre la caméra sur la machine.
2. **Le wrapper.** `zed-ros2-wrapper` de Stereolabs, en sous-module tiers dans `packages/`, sur une branche `zenith` de notre fork. La règle : on ne modifie un wrapper tiers que sur une branche à nous, avec le moins de changements possible, et on note dans `packages/README.md` ce qui a changé et pourquoi (question 5 : le lister).
3. **L'image.** Le wrapper construit sa propre image (`zed_ros2_l4t_36.4.0_sdk_5.1.0`) à partir de son dossier `docker/`, hors de nos Dockerfiles. Le nom encode la version de L4T et du SDK : c'est le contrat avec la Jetson. Le compose de notre dépôt ne fait que l'utiliser.
4. **Le compose.** `compose/zed.yml`, lu ligne par ligne : `runtime: nvidia`, `privileged`, `/dev` monté (la caméra est USB), `ipc: host` et `shm_size` (les images passent par la mémoire partagée), `network_mode: host`, domaine 2 et `ROS_LOCALHOST_ONLY=1` comme tout le monde. Le `command` : le launch du wrapper avec `camera_model`, le fichier de paramètres, et `publish_tf:=false` parce que la ZED n'est pas notre source de position.
5. **Les paramètres.** `config/zed.yaml`, un fichier de surcharge, pas une copie du fichier du wrapper. Ce qu'on a réglé et pourquoi : résolution 720 et facteur de réduction 2 (la Jetson suit), 15 images par seconde, `depth_mode: NONE` (pas de profondeur en 2026, le calcul coûte trop cher), suivi de position et cartographie désactivés (l'autopilote fait ça), détection d'objets du SDK désactivée (la vision est dans notre conteneur). La règle : chaque ligne de surcharge a un commentaire qui dit pourquoi.
6. **Le service.** `zed.service` attend `lsusb | grep stereolabs` avant de partir, `vision.service` vient après. Ce que ça donne au boot : la caméra branchée après le démarrage est quand même prise.

Puis le chemin du topic, pour fermer la boucle avec le fil conducteur : la ZED publie sur `/zed/...` (domaine 2, interne parce que pas préfixé `external`, donc jamais sur la radio), le conteneur vision s'y abonne, publie une détection `/aeac/internal/vision/...`, la mission la consomme. Les images ne traversent jamais la radio ; ce qui traverse est un résumé.

Séance : sur la Jetson, `make zed`, `ros2 topic hz /zed/zed_node/left/image_rect_color` (nom à vérifier), puis `make vision` et le topic de détection.

### 3. La fiche d'intégration

Une page à remplir, une question par décision :

| Décision | Question | ZED |
|---|---|---|
| Pilote | Sur la machine ou dans l'image ? Quelle version, liée à quoi ? | Machine, SDK lié à JetPack |
| Wrapper | Existe-t-il ? Fork ou tel quel ? Quelle branche ? | Fork, branche `zenith` |
| Image | La nôtre ou celle du wrapper ? Nom et version ? | Celle du wrapper |
| Compose | Périphériques, runtime, mémoire partagée, réseau ? | `/dev`, nvidia, `shm`, host |
| Paramètres | Fichier de surcharge dans `config/` ? Qu'est-ce qu'on coupe ? | `zed.yaml`, profondeur et SLAM coupés |
| Service | Attend quoi ? Vient après quoi ? | `lsusb`, après `lo-multicast` |
| Topics | Lesquels, internes ou externes, qui consomme ? | `/zed/...` internes, vision |

Exercice final : remplir la fiche pour un second capteur, au choix parmi ceux qui pourraient arriver en 2027 (question 6), en lisant la doc du fabricant. Produire le squelette : un `compose/<capteur>.yml`, un `config/<capteur>.yaml` commenté, un `systemd/<capteur>.service`, une cible `make`. Relu par un lead. C'est le geste exact qu'un membre fera quand un nouveau capteur arrivera.

### Quand ça casse (6.4)

| Symptôme | Cause probable | Remède |
|---|---|---|
| `zed.service` en `activating` | Caméra pas vue par `lsusb` | Câble USB 3, port, alimentation |
| Le conteneur démarre puis meurt | Version du SDK sur la Jetson différente de celle de l'image | Comparer `/usr/local/zed` et le nom de l'image |
| Topics ZED visibles, vision muette | Vision attend un autre nom de topic ou une autre résolution | `ros2 topic info`, `config/zed.yaml` |
| Images à 2 Hz | Résolution trop haute, ou profondeur activée par erreur | `config/zed.yaml` |

---

## 6. Matériel à produire

- Le compose « pont local » de 6.2 et `config/drones/local.json5` (à ajouter au template si on veut que l'exercice reste disponible dans tout dépôt de mission ; question 2).
- L'unité factice `formation.service` de 6.3, ou trois extraits de `journalctl` réels, selon la question 3.
- La liste des changements du fork `zenith` du wrapper ZED (question 5).
- Les captures : `docker logs` d'un pont en `retry` puis `connected`, `journalctl -b` d'un boot complet de la Jetson, `systemctl list-dependencies mission.service`.
- Le déroulé de la séance d'atelier (deux heures, un lead, le drone à l'atelier) : 6.1 `ping`, 6.3 boot et `journalctl`, 6.4 `make zed` et `make vision`.
- Une ligne dans `Control-Formations/README.md`.

---

## 7. Questions à trancher avant la rédaction

1. **Budget.** Le plan d'apprentissage ne détaille pas B6 au-delà de « contenu tel que défini ». Quatre documents plus une séance font environ 10 h de rédaction. Si c'est trop, 6.4 peut se réduire à la fiche et au chemin du topic, sans le second capteur.
2. **Le pont local dans le template.** L'exercice de 6.2 demande un compose et un `local.json5`. Soit ils vivent dans le dossier de la formation seulement, soit ils entrent dans `mission-template/` (`compose/bridge-local.yml`, `config/drones/local.json5`) et servent aussi à tester un pont sans drone dans aeac-2027. Recommandation : dans le template, c'est un outil de débogage utile aux leads.
3. **systemd sous WSL.** WSL2 sait démarrer systemd (`systemd=true` dans `/etc/wsl.conf`). Si la formation 2 l'active, l'unité factice de 6.3 devient possible sur le poste. Sinon, extraits de `journalctl` sur papier. À décider avec la formation 2.
4. **La séance d'atelier.** Obligatoire ou optionnelle ? Elle couvre les seuls jalons qui demandent la Jetson. Recommandation : une séance par cohorte, annoncée avec la formation, les jalons « séance » validés ce jour-là.
5. **Le fork `zenith` du wrapper ZED.** Le sous-module n'est pas initialisé sur le poste de Colin et la liste des changements par rapport à Stereolabs n'est écrite nulle part. À établir avec Haithem ou Nour avant de rédiger 6.4, et à mettre dans `packages/README.md`.
6. **Le second capteur.** Lequel donner en exercice ? Un capteur qui a une chance réelle d'arriver en 2027 (lidar, caméra thermique, nacelle SIYI par son SDK) vaut mieux qu'un exemple inventé. À choisir quand le thème AEAC 2027 est connu.
7. **Frontière avec B7.** Ce plan met en B7 tout ce qui touche à la Jetson elle-même (JetPack 5 contre 6, `ttyTHS0` et `ttyTHS1`, `dialout`, adresse statique, mDNS, Docker sur ARM). 6.3 et 6.4 y renvoient sans l'expliquer. À confirmer que B7 sera écrit, sinon deux paragraphes viennent ici.
8. **Nom du dossier.** Créé comme `6-reseau-zenoh-services/`. À renommer si le découpage change.
9. **Révision.** Comme pour la formation 5, Haithem Tebib et Nour Karoui (plan d'apprentissage). Le contenu 6.1 et 6.4 est celui qui dépend le plus de leur mémoire.
