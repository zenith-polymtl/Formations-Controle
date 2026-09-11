# Control-Formations

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

Commencer par [Formation 0](0-prerequis/0-prerequis-et-poste-de-travail.md), qui explique le parcours, où demander de l'aide et quoi poster à la fin de chaque module.

- [DEPANNAGE.md](DEPANNAGE.md) : les problèmes d'environnement (WSL, Docker, ports) qui reviennent dans tous les modules.
- [ANNEXE-SITL-DOCKER.md](ANNEXE-SITL-DOCKER.md) : le simulateur sans Mission Planner (Mac, expérimental).
- [plan_d'apprentissage.md](plan_d'apprentissage.md) : la carte complète du parcours, les formations 0 à 9, et ce qui vient après la formation 3.
