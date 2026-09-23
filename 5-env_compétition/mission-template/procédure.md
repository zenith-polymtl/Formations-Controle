# Procédure d'opération (jour J)

## Préparation

1. Manette allumée, batterie du portable chargée, radio SIYI alimentée.
2. Démarrer le portable GCS, ouvrir un terminal WSL dans le dépôt.
3. Démarrer la Jetson. Les services partent seuls (`make deploy` a été fait) ; attendre une minute.

## Démarrage

1. Se connecter au drone : `ssh zenith@192.168.144.30` (Hexa) ou `ssh zenith@192.168.144.31` (OS). Les adresses sont dans `ARCHITECTURE.md`.
2. Sur le drone, dans le dépôt : `make mission-status`, `make mavros-status`. Tout doit être `active (running)`.
3. Sur le portable : `make bag` dans un terminal (enregistrement), puis `make gcs C=<mission> DRONE=<drone>` dans un autre.
4. Vérifier que le sol voit le drone : `make shell IMG=gcs` puis `ros2 topic hz /aeac/external/<un topic de la mission>`.
5. Le pilote arme et décolle. Le code ne le fait jamais.

## Debug, dans l'ordre

1. **Côté drone, les topics** : `make shell IMG=drone` puis `ros2 topic list`. S'il manque des topics mavros : `make mavros-logs`. S'il manque des topics de la mission : `make mission-logs`.
2. **Un service** : `make <service>-status`, `make <service>-logs`, `make <service>-restart` pour `mavros`, `zed`, `zenoh-air`, `vision`, `mission`.
3. **Le sol ne voit rien** : `ros2 topic list` vide côté sol veut dire réseau. Vérifier dans l'ordre : `ping 192.168.144.30` (SIYI), `ping 100.87.171.82` (Tailscale), `docker logs aeac-zenoh-ground` (le pont se connecte-t-il ?), le `DRONE=` passé à `make gcs`.
4. **Pour reprendre la main** : `make undeploy` sur le drone, puis `make mavros` et `make drone C=<mission>` dans deux terminaux, logs à l'écran.

## Après le vol

1. `Ctrl-C` sur `make bag` ; le rosbag est dans `bags/` (ignoré par git).
2. Télécharger le log dataflash depuis Mission Planner (formation 9).
3. Une ligne dans `NOTES.md` : ce qui a marché, ce qui a cassé.
