# Les logs de la formation 9

Les fichiers `.bin` ne sont pas dans le dépôt (trop gros pour GitHub, et ignorés par git dans ce dossier). Ils se téléchargent depuis le Drive de l'équipe et se placent ici :

<!-- Lien de téléchargement à ajouter -->

| Fichier | Vol | Taille | Usage |
|---|---|---|---|
| `crash-proof-vol1-2026-08-08.bin` | Crash Proof, premier vol, 8 août 2026, 16 h 17, 24 min, 13 armements | 140 Mo | **Le log de la formation.** Tout 9.1 à 9.4 le suit. |
| `crash-proof-vol2-2026-08-11.bin` | Crash Proof, 11 août 2026, 16 h 58, 19 min | 135 Mo | Bonus de 9.4 seulement : vérifier si les corrections du vol 1 ont eu l'effet attendu. Vol très expérimental (Acro, limites d'angle à 80 degrés, glitchs GPS, failsafe batterie en fin de vol) : il ne sert pas de modèle. |
| `crash-proof-vol2a-2026-08-11-court.bin` | Crash Proof, 11 août 2026, 16 h 55, 2 min | 30 Mo | Un fichier court, pour tester qu'un outil charge. |

## Ce que contient le vol 1

- ArduCopter 4.6.3 sur MatekH743, quadricoptère en X, batterie 12S, DShot bidirectionnel (RPM par télémétrie ESC), pas de rangefinder.
- Stabilize jusqu'à 500 s (cinq sauts courts, coups de stick en roll et yaw vers 375 à 465 s), AltHold à partir de 501 s (deux essais qui finissent au sol à 706 et 770 s, puis des vols réussis après correction de `PSC_ACCZ_P` à 1049 s), Loiter à partir de 1183 s (dont deux minutes de vol calme entre 1218 et 1340 s), coups de stick en pitch vers 1430 s.
- Paramètres au début du vol : notch à 102 Hz en mode throttle, bandwidth 25, atténuation 15, harmoniques 1 et 3 ; passe-bas gyro à 42 Hz ; `ATC_RAT_RLL_P` et `ATC_RAT_PIT_P` 0,07, D 0,0018 ; `ATC_RAT_YAW_P` 0,18 ; `ATC_ANG_RLL_P` et `ATC_ANG_PIT_P` 4,5 ; `PSC_ACCZ_P` 0,015 puis 0,15 à 1049 s ; `MOT_SPIN_MIN` 0,07 puis 0,09 ; `MOT_THST_HOVER` 0,125.
- Journalisation : Fast Attitude, PID et IMU Fast actifs ; IMU 0 en batch, sans post-filtre.

## Ce que contient le vol 2

Paramètres appliqués après la séance du 11 août : `ATC_RAT_YAW_P` 0,24 ; `ATC_ANG_RLL_P` et `ATC_ANG_PIT_P` 4,05 ; `PSC_ACCZ_P` 0,18 ; notch à 111 Hz en mode télémétrie ESC, bandwidth 12, atténuation 6, options multisource, loop rate et toutes les IMU ; passe-bas gyro toujours à 42 Hz. Puis, en vol : `ANGLE_MAX` 80 degrés, `ACRO_RP_RATE` 680, `LOIT_SPEED` 36 m/s, `GPS_HDOP_GOOD` relevé pour pouvoir armer. Le vol se termine sur un failsafe batterie (RTL puis Land).
