# Le log de la formation 9

Le fichier `.bin` n'est pas dans le dépôt (217 Mo, trop gros pour GitHub, et ignoré par git dans ce dossier). Il se télécharge depuis le Drive de l'équipe et se place ici :

<!-- Lien de téléchargement à ajouter -->

| Fichier | Vol | Taille | Usage |
|---|---|---|---|
| `vol-tuning-2026-10-27.bin` | Vol de tuning du 27 octobre 2026, 14 h 15, environ 24 min, 13 armements | 217 Mo | **Le log de la formation.** Tout 9.1 à 9.4 le suit. |

Si le fichier téléchargé porte son nom d'origine, `2026-10-27 14-15-12.bin`, renommez-le.

## Ce que contient le vol

- ArduCopter 4.6.3 sur MatekH743 (firmware `-bdshot`), quadricoptère, batterie 12S, DShot bidirectionnel (RPM par télémétrie ESC), pas de rangefinder. C'est le Crash Proof, avec les réglages tirés de ses premiers vols d'août.
- Les temps sont en secondes depuis le démarrage du contrôleur, comme dans les outils.

| Temps (s) | Mode | Ce qui se passe |
|---|---|---|
| 146 à 332 | Stabilize, au sol | Contrôleur allumé, drone désarmé. |
| 333 à 480 | AltHold | **Premier vol : coups de stick en roll, puis pitch, puis yaw**, avec les réglages de départ. Batterie à 49,3 V. |
| 494 à 642 | AltHold, puis Loiter | Deux vols courts ; hover calme en Loiter de 573 à 593 s (filtres). |
| 658 à 717 | Stabilize, Loiter, AltHold | Vol plus libre, jusqu'à 12 m, gaz à fond en Stabilize à 699 s. |
| 736 à 972 | AltHold | **Le cas d'étude : `ATC_RAT_RLL_P` changé en vol six fois** (0,07, 0,098, 0,13, 0,04, 0,05, 0,03, puis retour à 0,07), avec des coups de roll après chaque changement. |
| 982 à 1 068 | AltHold | `ATC_ANG_PIT_P` passé de 4,05 à 3,0, coups de pitch, puis retour à 4,05. |
| 1 084 à 1 358 | Loiter, RTL | `ANGLE_MAX` monté à 60 puis 80 degrés : vol agressif, roulis jusqu'à 62 degrés. RTL commandé à 1 321 s. |
| 1 445 à 1 549 | Loiter, RTL | Deux vols courts ; failsafe batterie à 1 544 s (41,3 V). |

## Paramètres au début du vol

Notch harmonique en mode télémétrie ESC (3), `INS_HNTCH_FREQ` 111 Hz, bandwidth 12, atténuation 6, harmoniques 1 et 3, options 14 ; passe-bas gyro `INS_GYRO_FILTER` 42 Hz ; rates roll et pitch P 0,07, I 0,07, D 0,0018 ; yaw P 0,24, I 0,018, D 0 ; angles roll et pitch P 4,05 ; `PSC_ACCZ_P` 0,18, `PSC_ACCZ_I` 0,3 ; `MOT_SPIN_MIN` 0,09, `MOT_THST_HOVER` 0,125. Journalisation : Fast Attitude et PID actifs ; première IMU en batch, sans post-filtre (`INS_LOG_BAT_OPT` 0) ; `LOG_FILE_DSRMROT` 0, d'où un seul fichier pour 13 armements.
