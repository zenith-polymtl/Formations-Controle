# Images à produire pour la formation 9

Toutes viennent du même log, `crash-proof-vol1-2026-08-08.bin`, sauf mention. Les fichiers vont dans ce dossier, avec exactement ces noms ; les documents les référencent déjà. Une capture d'écran suffit ; les annotations (flèches, valeurs) se font dans n'importe quel outil.

## 9.1 lire un log

| Fichier | Contenu |
|---|---|
| `9.1-01-step-response-trois-cas.png` | Trois step responses côte à côte tirées de PID Review : le yaw (undershoot, plafonne à 0,78), le roll (correcte), et un overshoot (à prendre sur un autre log, ou dessiner les trois courbes à la main) |
| `9.1-02-chaine-controleurs.png` | Le schéma de la chaîne de contrôleurs (celui de la page Notion, revu) |
| `9.1-03-trois-outils.png` | UAV Log Viewer, PID Review et Filter Review avec le log chargé, en trois vignettes |
| `9.1-04-hardware-report.png` | Hardware Report : sections loop rate, charge CPU, voltage du contrôleur, messages perdus |
| `9.1-05-vibe-clip.png` | UAV Log Viewer : `VIBE.VibeX/Y/Z` et `VIBE.Clip` avec `CTUN.Alt` superposée, paliers de clip annotés (440, 706, 709, 770 s) |
| `9.1-06-esc-rpm-rcou.png` | `ESC[0].RPM` et `RCOU.C1` superposés sur une minute de vol : même forme |
| `9.1-07-bat-sag.png` | `BAT.Volt` sur tout le vol, avec le sag du décollage à 703 s (49,1 → 48,4) et un sag près de la fin annotés |

## 9.2 vibrations et filtres

| Fichier | Contenu |
|---|---|
| `9.2-01-selection-hover.png` | Filter Review, vue d'ensemble, plage 1 218 à 1 340 s sélectionnée |
| `9.2-02-spectre-pre-filtre.png` | Spectre pré-filtre, pics annotés à 114 et 350 Hz, petits pics, bosse de châssis |
| `9.2-03-post-filtre-initial.png` | Estimated post-filter avec les paramètres du log (moins 70 à 90 dB) contre pré-filtre |
| `9.2-04-notch-config.png` | Le panneau de configuration du notch, champs mode, options, fréquence, bandwidth, atténuation, harmoniques visibles |
| `9.2-05-trois-recalculs.png` | Trois recalculs : paramètres d'origine en mode 3 (trop), 114 Hz BW 10 ATT 5 (presque, moins 46), 112 Hz BW 12 ATT 5 (moins 51) |
| `9.2-06-spectrogramme.png` | Spectrogramme avec la trace moteur et les notches (moyenne en vert, zone grise des quatre notches) |
| `9.2-07-phase.png` | Retard de phase avant (200 degrés) et après (50 à 60) |
| `9.2-08-compare-params.png` | Mission Planner, Full Parameter List, Compare Params après un Load from file |

## 9.3 les rates

| Fichier | Contenu |
|---|---|
| `9.3-01-selection.png` | PID Review, vue d'ensemble, coups de stick sélectionnés (375 à 465 s pour roll et yaw ; 1 425 à 1 440 s pour pitch) |
| `9.3-02-roll-time.png` | Time domain rate roll zoomé, sommets 234 et 229 annotés |
| `9.3-03-pitch-time.png` | Time domain rate pitch, sommets 228 et 221 |
| `9.3-04-yaw-time.png` | Time domain rate yaw, sommets 146 et 121 |
| `9.3-05-step-responses.png` | Les trois step responses roll, pitch, yaw, ligne bleue lisible |
| `9.3-06-spectrogramme.png` | Spectrogramme PID Review avec la ligne bleue vers 110 Hz |

## 9.4 la chaîne complète et la démarche

| Fichier | Contenu |
|---|---|
| `9.4-01-att-roll.png` | `ATT.DesRoll` et `ATT.Roll` entre 438 et 465 s, mis à l'échelle, 18 et 19,4 annotés |
| `9.4-02-pida.png` | `PIDA.Tar` et `PIDA.Act` après 1 109 s, 440 et 330 annotés, zone bruitée entourée |
| `9.4-03-rcou.png` | `RCOU.C1` à `C4` pendant les coups de roll, pitch puis yaw, avec `MOT_SPIN_MIN` (1 090) tracé ; les moteurs s'écartent en yaw |
| `9.4-04-althold-episode.png` | `RCIN.C3`, `CTUN.Alt`, `CTUN.CRt`, `VIBE.Clip` entre 695 et 712 s, impact à 705,7 s annoté |
| `9.4-05-altitudes.png` | `CTUN.Alt`, `BARO.Alt`, `GPS.Alt` superposées avec les origines décalées |
