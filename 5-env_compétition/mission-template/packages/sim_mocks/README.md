# sim_mocks : ce qui remplace le matériel en simulation

Jamais lancé en vol, jamais inclus par un launch de mission. On les lance à la main, dans un second terminal (`make shell IMG=sim`), pendant que `make sim C=<mission>` tourne.

| Nœud | Remplace | Publie ou appelle | Commande |
|---|---|---|---|
| `rc_simulator` | La manette (interrupteurs) | `/mavros/rc/in` (`mavros_msgs/RCIn`), touches `w s x`, `e d c`, `r f v`, `q` pour quitter | `ros2 run sim_mocks rc_simulator` (lit le clavier : terminal au premier plan) |
| `target_mock` | Le conteneur vision (une détection) | `geometry_msgs/PointStamped` sur le topic donné en paramètre | `ros2 run sim_mocks target_mock --ros-args -p topic:=/aeac/internal/vision/target -p x:=5.0 -p y:=3.0` |
| `takeoff_test` | Le pilote (GUIDED, armement, décollage) | services `/mavros/set_mode`, `/mavros/cmd/arming`, `/mavros/cmd/takeoff` | `ros2 run sim_mocks takeoff_test --ros-args -p sim:=true -p alt:=10.0` |

Règle pour un nouveau mock : un fichier, un paramètre `topic`, pas de `time.sleep` dans un callback (utiliser un timer). Si un nœud de test doit armer ou changer de mode, il porte le suffixe `_test` et refuse de démarrer sans `sim:=true`, comme `takeoff_test`.
