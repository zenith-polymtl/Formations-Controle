# Déploiement sur la Jetson

systemd n'est qu'un emballage : chaque service lance le même `docker compose` qu'une cible `make` de la section 2 du Makefile. On déploie quand le drone doit démarrer seul au boot ; on ne déploie jamais sur un poste de développement.

1. Sur la Jetson, dans le dépôt : `make deploy C=<mission>`. Ça copie `systemd/*.service` dans `/etc/systemd/system/` en remplaçant `__REPO__` par le chemin du dépôt, écrit la mission dans `/etc/aeac/mission`, et active les six services.
2. Vérifier : `make mission-status`, `make mavros-logs`.
3. Changer de mission : `make deploy C=<autre>` (réécrit le fichier et redémarre).
4. Repasser en test à la main : `make undeploy`, puis `make mavros`, `make drone C=<mission>` dans des terminaux séparés.

Ordre au boot : `lo-multicast`, puis `mavros` (attend `/dev/ttyTHS1`), `zed` (attend la caméra), `zenoh-air`, `vision`, `mission`.
