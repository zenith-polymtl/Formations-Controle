# la formation 5 : l'environnement de compétition

Documents : [5.1](5.1-le-depot-vu-de-haut.md), [5.2](5.2-une-mission-en-simulation.md), [5.3](5.3-projet-ajouter-un-noeud.md), [annexe 5.4 (leads)](5.4-annexe-leads-creer-un-environnement.md), [5.5](5.5-pour-plus-tard.md).

Prérequis : formations 2 et 3. La formation 4 n'est pas nécessaire, le simulateur est celui de Mission Planner.

Objectifs :

- **le dépôt vu de haut** : qui tourne où (Jetson, radio, portable), ce qui est pour le drone et ce qui est pour le développement, où écrire (NOTES.md, procédure.md). Réussi si vous dessinez le schéma de mémoire.
- **le faire tourner pour la première fois** : clone, `make init`, `make build C=`, `make dev`. Réussi si `ros2 topic list` n'est pas vide dans le conteneur.
- **une mission en simulation** : `make sim C=demo`, `rc_simulator` dans un second terminal, `ros2 topic echo` dans un troisième. Réussi si la machine à états passe par ses quatre états sans drone.
- **la config** : mission, site, drone. Réussi si vous changez un waypoint sans toucher au code.
- **Docker, workspaces et sous-modules en gestes** : un Dockerfile par rôle et l'en-tête « ce qui diffère » ; une mission = un workspace, `make link` ; `make init`, `make status`, et si un paquet partagé est « modifié localement », demandez à un lead. Pas plus.
- **le Makefile en trois sections** : dev et sim, test sur véhicule, déploiement (à connaître, pas à pratiquer) ; `make help`, `C=`, `IMG=`, `DRONE=`, `SITE=`.
- **les règles** : le code n'arme jamais, seuls les nœuds `_test` sous `sim` ; `main` = ce qui vole, branche + PR, `make check` avant la PR.
