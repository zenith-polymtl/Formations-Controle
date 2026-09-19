# Journal de tuning : Crash Proof, vol 1, 8 août 2026

*Solution de la formation 9. À ouvrir après avoir écrit le vôtre. Les valeurs viennent du log `crash-proof-vol1-2026-08-08.bin` et de la séance d'analyse du 11 août 2026 ; ce qui a été appliqué se lit dans le log du vol suivant.*

## 1 - Le vol

- ArduCopter 4.6.3, MatekH743, quadricoptère en X, batterie 12S (50,2 V au départ), DShot bidirectionnel, pas de rangefinder.
- 24 minutes, 13 armements. Stabilize jusqu'à 500 s (cinq sauts, coups de stick en roll et yaw entre 375 et 465 s), AltHold à partir de 501 s (deux essais qui finissent au sol à 706 et 770 s ; vols réussis après 1 109 s), Loiter à partir de 1 183 s (hover calme de 1 218 à 1 340 s), coups de pitch vers 1 430 s.
- Paramètres changés en vol : `MOT_SPIN_ARM` 0,04 → 0,06 et `MOT_SPIN_MIN` 0,07 → 0,09 (588 à 590 s) ; `DISARM_DELAY` 2 → 15 s (678 s) ; `PSC_ACCZ_P` 0,015 → 0,15 et `PSC_ACCZ_I` 0,03 → 0,3 (1 049 s).

## 2 - Fiche de santé

| Vérification | Valeur | Verdict |
|---|---|---|
| Version, carte | 4.6.3, MatekH743-bdshot | |
| Loop rate | 400 Hz, pire cas 380 à 397 selon l'outil | sain |
| Charge CPU | 24 à 30 % | sain, à resurveiller après les notches |
| Voltage du contrôleur | 3,27 V stable | sain |
| Messages perdus | 0 | sain |
| Calibrations | compas OK ; pas de température ni de compas-moteurs | à faire sur le prochain drone, pas bloquant |
| VIBE moyennes (IMU 0) | X 0,7, Y 0,7, Z 1,2 m/s² | sain |
| VIBE maximales | X 31, Y 33, Z 55, aux impacts | sain hors impact |
| Clip | 75 (IMU 0), 36 (IMU 1) ; paliers à 440 s (atterrissage), 706 et 709 s (épisode AltHold), 770 s (deuxième essai) | expliqué par des contacts avec le sol |
| RPM en hover | environ 6 700 tr/min, soit 112 Hz | cohérent avec le pic du spectre |
| Pôles | 14 | cohérent |
| Température ESC | 45 °C en hover, 57 max | sain |
| Température contrôleur | jusqu'à 65 °C | à surveiller |
| Batterie | 50,2 V au départ, 46 V à la fin ; sag 0,7 V au décollage, 0,7 à 0,8 V près de la fin, jusqu'à 2 V sur les coups de gaz | sain |
| `BATT_ARM_VOLT` moins `BATT_LOW_VOLT` | 40,0 moins 40,8 = **négatif** | **problème** : viser 42 V |
| Courant batterie | 0,1 A constant : moniteur sans courant | **problème** hors tuning : configurer `BATT_MONITOR` ; le courant ESC dépanne (16 à 21 A par moteur) |
| Hover appris | 0,125 (plancher) : rapport poussée sur poids supérieur à 8 | à retenir pour les marges |
| GPS | 8 à 15 satellites, HAcc médiane 0,8 m, pas de glitch en vol | sain |
| Messages | alignements du yaw, un refus d'armer (gaz pas au neutre) | sain |
| Rangefinder | absent | pas d'estimé d'altitude fiable ; à installer |

**Verdict : sain, données fiables pour le tuning.** Deux corrections hors tuning (seuil d'armement, moniteur de courant), un capteur manquant (rangefinder).

## 3 - Filtres (Filter Review, hover 1 218 à 1 340 s)

| Paramètre | Avant | Hypothèse | Appliqué au vol 2 |
|---|---|---|---|
| `INS_HNTCH_MODE` | 1 (throttle) | 3 (télémétrie ESC) | oui |
| `INS_HNTCH_OPTS` | 0 | multi-source, loop rate, toutes les IMU (14) | oui |
| `INS_HNTCH_FREQ` | 102 Hz | 111 à 112 Hz | oui (111) |
| `INS_HNTCH_BW` | 25 | 12 | oui |
| `INS_HNTCH_ATT` | 15 dB | 5 dB | 6 |
| `INS_HNTCH_HMNCS` | 1 et 3 | inchangé (sans la 3e, un pic remonte à moins 43 dB) | oui |
| `INS_HNTCH_REF` | 1,0 | sans objet en mode 3 (en mode 1, aurait dû valoir 0,125) | |
| `INS_GYRO_FILTER` | 42 Hz | 400 Hz, à surveiller | **non, oublié** |
| `INS_LOG_BAT_OPT` | 0 | bit post-filtre pour le prochain vol | non |

Observation : sur-filtré à moins 70 et moins 90 dB, environ 200 degrés de retard de phase ; le passe-bas à 42 Hz lave tout ; le notch à 102 Hz est à côté du pic réel à 114. Après réglage : tous les pics sous moins 51 dB, phase à 50 ou 60 degrés.

## 4 - Rates (PID Review)

| Axe | Observation | Hypothèse | Appliqué au vol 2 | Résultat au vol 2 |
|---|---|---|---|---|
| Roll | 229 / 234, step response quasi idéale | rien | | rapport 1,04 : stable |
| Pitch | 221 / 228, léger undershoot (0,5 %, non significatif) | ratio P/D plus 3 à 5 % via D, à refaire batteries pleines | refait en vol, pas de changement de paramètre retenu | rapport 1,01 |
| Yaw | 121 / 146, step response plafonne à 0,78 | `ATC_RAT_YAW_P` plus 30 % | 0,18 → 0,24 (plus 33 %) | rapport 0,88 : mieux, encore sous 1, une autre hausse à prévoir |

Marge de contrôle pendant les coups de stick : minimum 1 250 en PWM pour un plancher à 1 090, maximum 1 552 sur le vol. Beaucoup de marge.

## 5 - Angles (UAV Log Viewer, `ATT`, 438 à 465 s)

| Axe | Observation | Hypothèse | Appliqué au vol 2 | Résultat au vol 2 |
|---|---|---|---|---|
| Roll | 19,4 / 18, overshoot 10 % | `ATC_ANG_RLL_P` moins 10 % | 4,5 → 4,05 | rapport 1,01 : overshoot disparu |
| Pitch | overshoot 10 % | `ATC_ANG_PIT_P` moins 10 % | 4,5 → 4,05 | rapport 1,02 |
| Yaw | un peu de délai, normal (rate yaw en manque de P) | rien | | |

## 6 - Chaîne verticale (après 1 109 s, AltHold et Loiter)

| Étage | Observation | Hypothèse | Appliqué au vol 2 | Résultat au vol 2 |
|---|---|---|---|---|
| Vitesse Z (`CTUN.DCRt` / `CRt`) | bien fité, pas assez de montées franches | rien ; montées et descentes franches au prochain vol | | |
| Accélération Z (`PIDA`) | 330 / 440, undershoot 20 à 25 % ; bruit 20 sur 250, à la limite | `PSC_ACCZ_P` plus 20 % ; envisager `FLTT`/`FLTD`/`FLTE` vers 15 Hz plus tard | 0,15 → 0,18 | rapport 0,83 (était 0,77) : mieux |
| Position Z (`CTUN.DAlt` / `Alt`) | pas assez de variations | rien | | |

## 7 - Chaîne horizontale (Loiter, 1 218 à 1 340 s et 1 438 s à la fin)

Aucun déplacement commandé : vitesse cible maximale 2 cm/s. Le maintien de position se regarde, rien ne se règle. Prochain vol : déplacements francs en Loiter, un axe à la fois, puis arrêts nets pour voir le freinage.

## 8 - Reconstruction de l'épisode AltHold (690 à 710 s)

1. 690 s : armé en AltHold, gaz à 987.
2. 697 à 702 s : le pilote monte les gaz jusqu'à 1 495 ; sous la moitié, le drone reste au sol, moteurs à 1 060.
3. 703,0 s : gaz à 1 555, décollage, montée à 0,8 m/s.
4. 703,5 s : le pilote ramène le stick à 1 313 (sous le centre) ; le drone monte à 2 m/s.
5. 704,0 s : stick à 1 257 ; le drone monte toujours (2,5 m).
6. 704,5 s : sommet à 3,1 m.
7. 705,0 s : le drone descend à 2,2 m/s ; le pilote monte les gaz à 1 508.
8. 705,5 s : gaz à 1 736 (87 %) ; le drone descend à 3,9 m/s ; throttle de sortie 0,09, sous le hover de 0,125.
9. 705,7 s : impact, `Clip` de 7 à 32.
10. 707,5 s : gaz coupés ; 708,1 s : désarmement ; 708,5 à 709 s : gaz remontés après désarmement ; 709,5 s : le drone bascule (roll 65 degrés, `Clip` à 57).

Cause : `PSC_ACCZ_P` à 0,015, dix fois trop bas. Le contrôleur d'accélération verticale ne suivait pas les demandes du pilote, avec un retard impossible à compenser à la main. Corrigé en vol à 1 049 s (0,15) ; les vols AltHold et Loiter suivants sont sans histoire. L'estimé d'altitude n'est plus fiable après l'impact (moins 5 m au sol).

Le récit du pilote (6 m, désarmement en l'air, réarmement tenté avant l'impact) et le log (3,1 m, impact avant désarmement, gaz remontés après) diffèrent. Le log fait foi sur les faits.

## 9 - Ce que le prochain vol doit contenir

1. Batteries pleines : hover calme 30 à 40 s, puis coups de stick roll, pitch, yaw, **en début de vol**.
2. `INS_LOG_BAT_OPT` avec le bit post-filtre, `LOG_FILE_DSRMROT` à 1.
3. Le passe-bas gyro réellement à 400 Hz, vérifié par deux comparaisons.
4. AltHold avec montées et descentes franches (vitesse Z, position Z).
5. Loiter avec déplacements francs et arrêts nets (vitesse XY, position XY).
6. `BATT_ARM_VOLT` à 42 V ; moniteur de courant configuré ; rangefinder installé ou, à défaut, noté comme absent.
7. Surveiller la charge CPU (notches), les micro-oscillations (passe-bas agressif) et le clipping.

## 10 - Ce que le vol 2 a montré (bonus)

Vol très expérimental, à ne pas prendre pour modèle. Sur les hypothèses du vol 1 : angles confirmés (1,01 et 1,02), yaw amélioré mais pas fini (0,88), accélération verticale améliorée (0,83), passe-bas non appliqué. Hors tuning : glitchs GPS répétés avec changements d'IMU par l'EKF, moteurs au plafond pendant les manœuvres en Acro à 680 degrés par seconde et avec `ANGLE_MAX` à 80 degrés, `GPS_HDOP_GOOD` relevé pour armer, et failsafe batterie en fin de vol (37,5 V puis 29,6 V, effondrement de 41 à 22 V en vingt secondes). Le journal du vol 2 commence par la batterie.
