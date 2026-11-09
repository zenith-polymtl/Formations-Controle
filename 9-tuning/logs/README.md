# Les logs de la formation 9

Les fichiers `.bin` ne sont pas dans le dépôt (trop gros pour GitHub, et ignorés par git dans ce dossier). Ils se téléchargent depuis le Drive de l'équipe et se placent ici :

<!-- Lien de téléchargement à ajouter -->

| Fichier | Vol | Taille | Usage |
|---|---|---|---|
| `vol-tuning-2026-10-27.bin` | Vol de tuning du 27 octobre 2026, environ 24 min | 217 Mo | **Le log de la formation.** Tout 9.1 à 9.4 le suit. |
| `vol-corrige-2026-10-28.bin` | Le lendemain, même drone, avec les correctifs | 130 Mo | Les références « à quoi ça devrait ressembler » (9.2, 9.3, 9.4). |

Si les fichiers téléchargés portent leur nom d'origine (`2026-10-27 14-15-12.bin`, `2026-10-28 17-03-22.bin`), renommez-les.

## Le vol du 27 octobre

Le Crash Proof : ArduCopter 4.6.3, quadricoptère, batterie 12S, RPM des moteurs par télémétrie ESC. Les temps sont en secondes depuis le démarrage du contrôleur, comme dans les outils.

| Temps (s) | Mode | Ce qui se passe |
|---|---|---|
| 350 à 395 | AltHold | Hover calme (filtres) |
| 395 à 470 | AltHold | Coups de stick en roll, pitch, yaw, avec les réglages de départ |
| 736 à 972 | AltHold | `ATC_RAT_RLL_P` changé en vol (0,07, 0,098, 0,13, 0,04, 0,05, 0,03, puis 0,07), avec des coups de roll après chaque changement |

Réglages de départ : passe-bas gyro 42 Hz ; notch en mode télémétrie ESC, plancher 111 Hz ; rates roll et pitch P 0,07, I 0,07, D 0,0018 ; yaw P 0,24 ; angles P 4,05 ; `PSC_ACCZ_P` 0,18.

## Le vol du 28 octobre

| Temps (s) | Mode | Ce qui se passe |
|---|---|---|
| 301 à 465 | AltHold | Coups de stick roll, pitch, yaw ; hover à 10 m de 352 à 364 s ; montées et descentes franches de 404 à 438 s |

Ce qui a changé depuis le 27 : passe-bas gyro 400 Hz ; plancher du notch 107 Hz ; rate yaw P 0,35 ; angles P 3,7 ; `PSC_ACCZ_P` 0,25 ; rates roll et pitch 0,068.
