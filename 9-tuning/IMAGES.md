# Images de la formation 9

Toutes viennent du log du vol de tuning du 27 octobre 2026 (`logs/vol-tuning-2026-10-27.bin`) et sont dans `images/`. Ce sont des exports des outils eux-mêmes (PID Review, Filter Review, UAV Log Viewer, Hardware Report), pas des graphiques refaits : une recrue qui charge le log doit voir la même chose. Seuls les titres des graphiques et les noms des « Test » de PID Review ont été renommés en français.

Pour refaire une image : charger le log dans l'outil, régler la plage de temps et les champs indiqués, puis exporter (icône appareil photo de la barre Plotly).

## 9.1 lire un log

| Fichier | Outil | Contenu |
|---|---|---|
| `9.1-01-uav-log-viewer-interface.png` | UAV Log Viewer | Interface avec le log chargé, `CTUN.Alt` tracé, bandes de modes |
| `9.1-02-vue-ensemble-altitude-batterie.png` | UAV Log Viewer | `CTUN.Alt` et `BAT.Volt` sur tout le vol |
| `9.1-03-hardware-report-loop-rate.png` | Hardware Report | Loop rate moyen et pire cas |
| `9.1-04-hardware-report-cpu.png` | Hardware Report | Charge CPU |
| `9.1-05-hardware-report-voltage.png` | Hardware Report | Voltage du contrôleur (non référencée dans le texte) |
| `9.1-06-hardware-report-messages-perdus.png` | Hardware Report | Messages perdus (non référencée dans le texte) |
| `9.1-07-vibe-clip.png` | UAV Log Viewer | `VIBE[0].VibeX/Y/Z`, `VIBE[0].Clip`, `CTUN.Alt` |
| `9.1-08-esc-rpm-rcou.png` | UAV Log Viewer | `ESC[0].RPM` et `RCOU.C1`, 395 à 470 s |

## 9.2 vibrations et filtres

| Fichier | Outil | Contenu |
|---|---|---|
| `9.2-01-selection-loiter-calme.png` | Filter Review | Vue d'ensemble du vol |
| `9.2-02-spectre-pre-filtre.png` | Filter Review | Spectre pré-filtre, 350 à 395 s (hover en AltHold) |
| `9.2-03-post-filtre-parametres-du-vol.png` | Filter Review | Pré-filtre et post-filtre estimé, paramètres du vol (passe-bas 42 Hz) |
| `9.2-05-passe-bas-400.png` | Filter Review | Passe-bas à 400 Hz, notch d'origine (111 Hz) affiché |
| `9.2-06-reglage-propose.png` | Filter Review | Plancher du notch à 100 Hz, passe-bas 400 Hz |
| `9.2-07-spectrogramme.png` | Filter Review | Spectrogramme, notch fondamental plat à 111 Hz, harmonique 3 qui suit le RPM |
| `9.2-08-phase-avant.png` | Filter Review | Amplitude et phase des filtres du vol |
| `9.2-09-phase-apres.png` | Filter Review | Amplitude et phase du réglage proposé |
| `9.2-10-spectrogramme-propose.png` | Filter Review | Spectrogramme avec le réglage proposé : le notch suit chaque moteur |

## 9.3 les rates

| Fichier | Outil | Contenu |
|---|---|---|
| `9.3-01-vue-ensemble.png` | PID Review | Flight Data, tout le vol |
| `9.3-02-roll-time.png` à `9.3-04-yaw-time.png` | PID Review | Time domain PIDR, PIDP, PIDY, premier vol (fenêtres de 4 s) |
| `9.3-05-step-roll.png` à `9.3-07-step-yaw.png` | PID Review | Step response PIDR, PIDP, PIDY, 333 à 479 s |
| `9.3-08-step-roll-sept-reglages.png` | PID Review | Step response PIDR sur tout le vol, un « Test » par valeur de `ATC_RAT_RLL_P` |
| `9.3-09` à `9.3-14-roll-time-*.png` | PID Review | Time domain PIDR, 4 s de coups de stick par réglage (0,07 ; 0,098 ; 0,13 ; 0,05 ; 0,03 ; retour à 0,07) |

## 9.4 la chaîne complète et la démarche

| Fichier | Outil | Contenu |
|---|---|---|
| `9.4-01-att-pitch-p405.png` | UAV Log Viewer | `ATT.DesPitch` et `ATT.Pitch`, même axe, 408 à 418 s (`ATC_ANG_PIT_P` 4,05) |
| `9.4-02-att-pitch-p3.png` | UAV Log Viewer | Idem, 1 005 à 1 015 s (`ATC_ANG_PIT_P` 3,0) |
| `9.4-03-ctun-althold.png` | UAV Log Viewer | `CTUN.DCRt`, `CRt`, `DAlt`, `Alt`, 333 à 480 s |
| `9.4-04-rcou-coups-de-stick.png` | UAV Log Viewer | `RCOU.C1` à `C4`, 395 à 470 s |
| `9.4-05-extrait-agressif.png` | UAV Log Viewer | `ATT.DesRoll`, `ATT.Roll`, `RCOU.C1`, `C2`, 1 270 à 1 300 s |

## Ce qui reste à faire à la main

Captures d'écran d'interface, que l'export Plotly ne couvre pas :

| Fichier à produire | Contenu | Où dans le texte |
|---|---|---|
| `9.2-10-notch-config.png` | Filter Review, le panneau de configuration du notch (mode, fréquence, bandwidth, atténuation, harmoniques, options) | 9.2, section 6 |
| `9.2-11-compare-params.png` | Mission Planner, Full Parameter List, Compare Params après un Load from file | 9.2, section 8 |
| `9.1-09-chaine-controleurs.png` | Le schéma de la chaîne de contrôleurs (celui de la page Notion, revu) ; le texte a pour l'instant un schéma en texte | 9.1, section 1.4 |
