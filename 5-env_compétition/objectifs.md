# la formation 5 : l'environnement de compétition

Documents : [5.1](5.1-le-depot-vu-de-haut.md), [5.2](5.2-une-mission-en-simulation.md), [5.3](5.3-projet-ajouter-un-noeud.md), [annexe 5.4 (leads)](5.4-annexe-leads-creer-un-environnement.md), [5.5](5.5-pour-plus-tard.md).

Prérequis : formations 2 et 3. La formation 4 n'est pas nécessaire, le simulateur est celui de Mission Planner.

Objectifs :

- **le repo vu de haut** : qui tourne où (Jetson, radio, portable), ce qui est pour le drone et ce qui est pour le développement, où écrire (`NOTES.md`, `procédure.md`). Réussi si vous dessinez le schéma de mémoire.
- **le faire tourner pour la première fois** : clone, `make init`, `make build C=`, `make dev`. Réussi si `ros2 topic list` répond dans le conteneur, sans rien sourcer à la main.
- **une mission en simulation** : `make sim C=demo`, puis `make takeoff` et `make rc` dans un second terminal, `make echo T=` dans un troisième. Réussi si la machine à états passe par ses quatre états sans drone.
- **la config** : mission, site, drone. Réussi si vous changez un waypoint sans toucher au code, et si `make sim C=demo SITE=cimetiere` part du bon terrain.
- **Docker, workspaces et submodules en gestes** : un Dockerfile par rôle et l'en-tête « ce qui diffère » ; une mission a son workspace, et les liens vers les packages partagés y sont déjà posés ; `make init`, `make status`, et si un package partagé est « modifié localement », demandez à un lead. Pas plus.
- **le Makefile en trois sections** : dev et sim, test sur véhicule, déploiement (à connaître, pas à pratiquer) ; `make help`, `C=`, `SITE=`, `T=`, et `IMG=` seulement pour viser un autre conteneur (`make logs IMG=mavros-sim`). Une commande qu'on retape souvent devient une cible.
- **les règles** : le code de mission n'arme jamais, seuls les nodes `*_test` de `sim_mocks` le font et aucun launch file de mission ne les inclut ; `main` = ce qui vole, une branche puis une PR, `make check` avant la PR.
