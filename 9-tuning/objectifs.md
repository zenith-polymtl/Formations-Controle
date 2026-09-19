# La formation 9 : tuning et analyse post-vol

Branche parallèle du parcours : elle se fait après la formation 1 et ne demande ni Docker ni ROS 2. Un seul log réel, le premier vol du Crash Proof (8 août 2026), est suivi du début à la fin ; les conclusions de la formation sont celles qui ont réellement été appliquées sur le drone trois jours plus tard.

Objectifs, par document :

- **la formation 9.1, lire un log** : préparer un vol de tuning (options de log, consignes au pilote, failsafes minimaux), distinguer `.bin` et `.tlog`, ouvrir un log dans les trois outils web d'ArduPilot, situer les contrôleurs de la chaîne, remplir la fiche de santé du système avant toute conclusion.
- **la formation 9.2, vibrations et filtres** : lire un spectre, placer le notch harmonique et le passe-bas gyro dans Filter Review avec la cible de moins 50 dB, exporter, importer et vérifier les paramètres.
- **la formation 9.3, les rates** : lire target contre actual et la step response dans PID Review, décider quel gain bouger, dans quel sens et de combien, comprendre le cas du yaw.
- **la formation 9.4, la chaîne complète et la démarche** : angle, vertical et horizontal dans UAV Log Viewer avec la fiche des contrôleurs, la marge de contrôle des moteurs, le journal d'hypothèses et l'ordre des vols, la reconstruction d'un vol qui a mal tourné.

Annexes : [fiche-controleurs.md](fiche-controleurs.md) (messages de log et paramètres de chaque contrôleur), [glossaire.md](glossaire.md), [logs/README.md](logs/README.md) (les logs de travail), [solutions/](solutions/) (le journal complet du vol 1).

Les rosbags (enregistrement et relecture côté ROS 2) ne sont pas traités ici : ils relèvent de la formation 3.
