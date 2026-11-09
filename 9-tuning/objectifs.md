# La formation 9 : tuning et analyse post-vol

Branche parallèle du parcours : elle se fait après la formation 1 et ne demande ni Docker ni ROS 2. Un seul vol est suivi du début à la fin : **le vol de tuning du 27 octobre 2026**, un vol type. On y voit les phases d'un vol de tuning, les coups de stick axe par axe, et un même gain changé en vol pour comparer un drone mou, juste et trop nerveux. Le vol du lendemain, avec les correctifs, sert de référence : à quoi ça devrait ressembler.

> [!NOTE]
> **À quoi ça sert en compétition**
> Un drone de compétition vole en mode autonome (Guided, Auto) : toute la chaîne de contrôleurs travaille, et chaque défaut de réglage se voit dans la précision de la trajectoire, la stabilité de la caméra et la consommation de la batterie. Un drone mal filtré chauffe ses moteurs ; un rate trop nerveux fait trembler l'image ; un contrôleur vertical trop mou rate un atterrissage. Et le jour où un vol tourne mal, c'est le log qui dit pourquoi. Cette formation apprend à lire ce log et à décider quoi changer.

Objectifs, par document :

- **la formation 9.1, lire un log** : ce qu'un contrôleur essaie de faire, comment se déroule un vol de tuning type, les trois outils web d'ArduPilot, la fiche de santé du système avant toute conclusion.
- **la formation 9.2, vibrations et filtres** : lire un spectre, placer le notch harmonique et le passe-bas gyro dans Filter Review avec la cible de moins 50 dB.
- **la formation 9.3, les rates** : lire target contre actual et la step response dans PID Review, puis comparer plusieurs réglages du même gain pris dans un même vol et choisir le bon.
- **la formation 9.4, la chaîne complète et la démarche** : angle, vertical et horizontal, la marge de contrôle des moteurs, le journal d'hypothèses, et ce que le vol suivant a montré.

Annexes : [fiche-controleurs.md](fiche-controleurs.md) (messages de log et paramètres de chaque contrôleur), [glossaire.md](glossaire.md), [logs/README.md](logs/README.md) (le log de travail), [solutions/](solutions/) (le journal complet du vol du 27 octobre).

Les rosbags (enregistrement et relecture côté ROS 2) ne sont pas traités ici : l'enregistrement est vu en formation 4 (4.2, section 4, `make bag`).
