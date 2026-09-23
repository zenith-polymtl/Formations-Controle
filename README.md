# Formations-Controle

Le parcours de formation de l'équipe contrôle de Zenith : du premier drone simulé jusqu'à une node ROS 2 qui pilote le drone, dans l'environnement exact du dépôt de compétition. Les documents se lisent directement ici, sur GitHub ; le dépôt se clone dans la formation 2.

| Module | Sujet | Durée |
|---|---|---|
| [Formation 0](0-prerequis/0-prerequis-et-poste-de-travail.md) | Prérequis et poste de travail : terminal, Git, Python orienté objet, réseau | 1 h |
| [Formation 1](1-premier-drone/1-mission-planner-et-zenmav.md) | Premier contact : Mission Planner, la simulation, MAVLink, un script Zenmav | 2 h |
| [Formation 2](2-environnement/2-wsl-docker-compose-make.md) | Environnement de travail : WSL, Docker, Compose, Make, mavros dans un conteneur | 3 h |
| [Formation 3.1](3-ros2/3.1-premiers-pas-ros2.md) | ROS 2 : nodes, topics, workspace, publisher et subscriber | 2 h |
| [Formation 3.2](3-ros2/3.2-launch-parametres-services.md) | ROS 2 : launch, paramètres, services | 1 h 30 |
| [Formation 3.3](3-ros2/3.3-mavros.md) | mavros : topics et services, décollage depuis le terminal, messages à demander | 1 h 30 |
| [Formation 3.4](3-ros2/3.4-piloter-au-clavier.md) | Projet : piloter le drone au clavier avec une node maison | 2 h 30 |
| [Formation 5.1](5-env_compétition/5.1-le-depot-vu-de-haut.md) | L'environnement de compétition : le dépôt de mission vu de haut, Makefile, sous-modules | 1 h 45 |
| [Formation 5.2](5-env_compétition/5.2-une-mission-en-simulation.md) | Une mission en simulation : `make sim`, la config mission, site et drone, trois pannes | 2 h 30 |
| [Formation 5.3](5-env_compétition/5.3-projet-ajouter-un-noeud.md) | Projet : ajouter un nœud à la démo, `make check`, branche et PR | 2 h |
| [Annexe 5.4](5-env_compétition/5.4-annexe-leads-creer-un-environnement.md) | Créer et faire évoluer un dépôt de mission : leads | 20 min |
| [Formation 5.5](5-env_compétition/5.5-pour-plus-tard.md) | Pour plus tard : l'annexe des leads, `procédure.md`, la formation 6, la vision. Lecture | 10 min |
| [Formation 9.1](9-tuning/9.1-lire-un-log.md) | Tuning : préparer un vol, lire un log, les trois outils, la fiche de santé | 1 h 30 |
| [Formation 9.2](9-tuning/9.2-vibrations-et-filtres.md) | Tuning : vibrations, notch harmonique et passe-bas dans Filter Review | 1 h 30 |
| [Formation 9.3](9-tuning/9.3-les-rates.md) | Tuning : les rates dans PID Review, step response, ratio P sur D, le yaw | 1 h 30 |
| [Formation 9.4](9-tuning/9.4-chaine-complete-et-demarche.md) | Tuning : angle, vertical, horizontal, marge moteur, journal d'hypothèses, lire un vol raté | 2 h |

La formation 9 est une branche parallèle : elle se fait après la formation 1 et ne demande ni Docker ni ROS 2. Elle suit un seul log réel, le premier vol du Crash Proof.

Commencer par [Formation 0](0-prerequis/0-prerequis-et-poste-de-travail.md), qui explique le parcours, où demander de l'aide et quoi poster à la fin de chaque module.

- [DEPANNAGE.md](DEPANNAGE.md) : les problèmes d'environnement (WSL, Docker, ports) qui reviennent dans tous les modules.
- [ANNEXE-SITL-DOCKER.md](ANNEXE-SITL-DOCKER.md) : le simulateur sans Mission Planner (Mac, expérimental).
