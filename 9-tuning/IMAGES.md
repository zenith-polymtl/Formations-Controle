# Images de la formation 9

Les images sont dans `images/`. Ce sont des exports des outils eux-mêmes (PID Review, Filter Review, UAV Log Viewer, Hardware Report) chargés avec les logs de [logs/README.md](logs/README.md), pas des graphiques refaits. Seuls les titres ont été mis en français. Les images marquées « 28 oct. » viennent du vol corrigé et servent de référence.

Pour refaire une image : charger le log dans l'outil, régler la plage de temps et les champs, puis exporter (icône appareil photo de la barre du graphique).

| Fichier | Outil | Contenu |
|---|---|---|
| `9.1-01-uav-log-viewer-interface.png` | UAV Log Viewer | Interface, `CTUN.Alt` et bandes de modes |
| `9.1-02-vue-ensemble-altitude-batterie.png` | UAV Log Viewer | `CTUN.Alt` et `BAT.Volt`, tout le vol |
| `9.1-03-hardware-report-loop-rate.png` | Hardware Report | Loop rate |
| `9.1-04-vibe-clip.png` | UAV Log Viewer | `VIBE` X, Y, Z, `Clip`, `CTUN.Alt` |
| `9.1-05-esc-rpm-rcou.png` | UAV Log Viewer | `ESC[0].RPM` et `RCOU.C1`, 395 à 470 s |
| `9.2-01-vue-ensemble.png` | Filter Review | Vue d'ensemble |
| `9.2-02-spectre-pre-filtre.png` | Filter Review | Pré-filtre, 350 à 395 s |
| `9.2-03-post-filtre-parametres-du-vol.png` | Filter Review | Post-filtre estimé, filtres du vol |
| `9.2-04-passe-bas-400.png` | Filter Review | Passe-bas 400 Hz, notch du vol |
| `9.2-05-reglage-propose.png` | Filter Review | Plancher du notch 100 Hz, passe-bas 400 Hz |
| `9.2-06-spectrogramme.png` | Filter Review | Notch bloqué à 111 Hz |
| `9.2-07-phase-avant.png`, `9.2-08-phase-apres.png` | Filter Review | Amplitude et phase des filtres |
| `9.2-09-reference-28-oct-spectre.png` | Filter Review | 28 oct. : spectre après correctifs |
| `9.3-01-vue-ensemble.png` | PID Review | Vue d'ensemble |
| `9.3-02-roll-time.png`, `9.3-03-yaw-time.png` | PID Review | Time domain, premier vol |
| `9.3-04-step-roll.png`, `9.3-05-step-yaw.png` | PID Review | Step response, 333 à 479 s |
| `9.3-06-step-roll-sept-reglages.png` | PID Review | Step response roll, un « Test » par réglage de P |
| `9.3-07-roll-time-p007.png`, `9.3-08-roll-time-p013.png` | PID Review | Time domain roll à P 0,07 et 0,13 |
| `9.3-09-reference-28-oct-step-yaw.png` | PID Review | 28 oct. : step response yaw, P 0,35 |
| `9.4-01-att-pitch-p405.png` | UAV Log Viewer | `ATT.DesPitch` et `ATT.Pitch`, premier vol |
| `9.4-02-rcou-coups-de-stick.png` | UAV Log Viewer | `RCOU.C1` à `C4`, 395 à 470 s |
| `9.4-03-reference-28-oct-vertical.png` | UAV Log Viewer | 28 oct. : `CTUN.DCRt`, `CRt`, `DAlt`, `Alt`, 400 à 440 s |

À faire à la main, si on veut les ajouter : le panneau de configuration du notch dans Filter Review, Compare Params dans Mission Planner, et le schéma de la chaîne de contrôleurs.
