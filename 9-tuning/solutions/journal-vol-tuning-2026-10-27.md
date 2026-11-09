# Journal de tuning : Crash Proof, vol du 27 octobre 2026

*Solution de la formation 9. À ouvrir après avoir écrit le vôtre. Les valeurs viennent du log `vol-tuning-2026-10-27.bin`, lues dans PID Review, Filter Review, UAV Log Viewer et le Hardware Report, et recoupées par script.*

## 1 - Le vol

- ArduCopter 4.6.3, MatekH743-bdshot, quadricoptère, batterie 12S (49,5 V au premier armement), DShot bidirectionnel, pas de rangefinder.
- Environ 24 minutes, 13 armements, un seul fichier (`LOG_FILE_DSRMROT` à 0).
- Phases : coups de stick roll, pitch, yaw en AltHold (333 à 480 s) ; hover calme en Loiter (573 à 593 s) ; vol libre (658 à 717 s) ; sept réglages de `ATC_RAT_RLL_P` en AltHold (736 à 972 s) ; `ATC_ANG_PIT_P` à 3,0 (982 à 1 068 s) ; vol agressif en Loiter (1 084 à 1 358 s) ; deux vols courts et failsafe batterie (1 445 à 1 549 s).
- Paramètres changés en vol : `ATC_RAT_RLL_P` (six fois), `ATC_ANG_PIT_P` (deux fois), `ANGLE_MAX` 30 → 60 → 80 degrés, `LAND_ALT_LOW`, `LAND_SPEED_HIGH`, `RTL_ALT` 20 → 10 m.

## 2 - Fiche de santé

| Vérification | Valeur | Verdict |
|---|---|---|
| Version, carte | 4.6.3, MatekH743-bdshot | |
| Loop rate | moyenne 397 à 400 Hz ; pire boucle isolée 7,5 ms | sain |
| Charge CPU | 24 à 34 %, 29 % en moyenne | sain, à resurveiller après les filtres |
| Voltage du contrôleur | 3,25 à 3,34 V | sain |
| Messages perdus | 0 | sain |
| Calibrations | compas OK ; pas de température IMU ni de compas contre moteurs | pas bloquant |
| Paramètres changés en vol | voir section 1 | |
| VIBE (IMU 0) | moyennes X 1,2, Y 1,0, Z 1,5 m/s² ; max 14 m/s² à 1 247 s | sain |
| Clip | 0 | sain |
| RPM en hover | 6 260 à 6 500 tr/min, soit 104 à 108 Hz | cohérent avec le pic du spectre |
| Pôles | 14 | cohérent |
| Température ESC | 34 °C max | sain |
| Batterie | 49,5 V au départ, 41,5 V à la fin ; failsafe batterie à 1 544 s (41,3 V) | sain ; vol mené jusqu'au seuil |
| `BATT_ARM_VOLT` moins `BATT_LOW_VOLT` | 40,0 moins 42,0 = **négatif** | **problème** : viser environ 43 V |
| Courant batterie | 0,1 A constant | **problème** hors tuning : configurer `BATT_MONITOR` ; `ESC.Curr` dépanne |
| Journalisation | pas de post-filtre (`INS_LOG_BAT_OPT` 0), un seul fichier | à corriger |
| Hover appris | 0,125 (plancher) | à retenir pour les marges |
| GPS | 11 à 16 satellites, pas de glitch | sain |
| Messages | alignements du yaw au décollage ; failsafes batterie et radio à la fin | sain |

**Verdict : sain, données fiables pour le tuning.** Deux corrections hors tuning (seuil d'armement, moniteur de courant), deux réglages de journalisation à corriger.

## 3 - Filtres (Filter Review, 573 à 593 s)

| Paramètre | Pendant le vol | Hypothèse |
|---|---|---|
| `INS_GYRO_FILTER` | 42 Hz | 400 Hz, à surveiller |
| `INS_HNTCH_FREQ` | 111 Hz | 107 Hz (le plancher doit être sous le hover) |
| `INS_HNTCH_MODE`, `_OPTS`, `_BW`, `_ATT`, `_HMNCS` | 3, 14, 12, 6, 5 | inchangés |
| `INS_LOG_BAT_OPT` | 0 | bit post-filtre |

Observation : pics pré-filtre à 107 Hz (moins 36 dB), 310 à 320 Hz (moins 41) et 640 Hz (moins 45). Avec les paramètres du vol, tout est écrasé sous moins 60 dB par le passe-bas à 42 Hz (phase environ moins 115 degrés à 50 Hz). Passe-bas à 400 Hz : le pic moteur remonte à moins 46 dB, parce que le notch reste bloqué à son plancher de 111 Hz (spectrogramme). Notch à 107 Hz : moins 54 et moins 53 dB, phase environ moins 18 degrés à 50 Hz.

## 4 - Rates (PID Review)

### 4.1 - Phase 1, réglages de départ (333 à 479 s)

| Axe | Step response (sommet, fin) | Lecture | Hypothèse |
|---|---|---|---|
| Roll | 0,91, 0,88 | léger undershoot | voir 4.2 |
| Pitch | 0,89, 0,85 | léger undershoot | `ATC_RAT_PIT_P` 0,085, à vérifier |
| Yaw | 0,77, 0,77 | undershoot net | `ATC_RAT_YAW_P` plus 30 à 40 % (environ 0,32), par étapes, marge moteur à surveiller |

### 4.2 - Phase 3, sept réglages de `ATC_RAT_RLL_P`

| Test | P | Sommet | Montée à 80 % | Lecture |
|---|---|---|---|---|
| 1 | 0,07 | 0,83 | 40 ms | undershoot |
| 2 | 0,098 | 1,03 | 27 ms | rapide, petit dépassement, un creux |
| 3 | 0,13 | 1,07 | 22 ms | oscillation à environ 14 Hz |
| 4 | 0,04 | | | 5 s sans coup de stick : rien à calculer |
| 5 | 0,05 | 0,89 | 42 ms | undershoot, lent |
| 6 | 0,03 | 0,94 (1,00 à 0,5 s) | 55 ms | lent ; contredit par le time domain (185 pour 199), on ne conclut pas |
| 7 | 0,07 | 0,85 | 40 ms | répète le Test 1 |

Hypothèse : `ATC_RAT_RLL_P` **0,085** (plus 20 %), D inchangé à 0,0018. Le plafond restant sous 1 relève du I et du feed-forward, vers le troisième vol.

## 5 - Angles (UAV Log Viewer, `ATT`)

| Axe | Observation | Hypothèse |
|---|---|---|
| Pitch | `ATC_ANG_PIT_P` 4,05 et 3,0 : même overshoot d'environ 10 % (médianes 1,11 et 1,09), pas de différence mesurable ; `ATT` à 10 Hz | rien ; refaire avec de petites corrections si besoin |
| Roll | overshoot d'environ 10 %, y compris à 60 degrés | rien tant que le rate n'est pas réglé |

## 6 - Chaîne verticale (premier vol, AltHold)

Vitesse verticale bien suivie (pente 0,94) ; plus ou moins 0,7 m/s seulement, altitude entre 0 et 3,3 m. Rien à régler ; montées et descentes franches au prochain vol.

## 7 - Chaîne horizontale

Aucun déplacement franc commandé en Loiter. Rien à régler ; déplacements francs et arrêts nets au prochain vol.

## 8 - Marge de contrôle

Pendant les coups de stick : roll 1 229 à 1 349, pitch 1 179 à 1 357, yaw **1 136** à 1 392, pour un plancher à 1 090. Le yaw laisse 46 points de marge en bas : la hausse du P yaw se fait par étapes. Vol agressif : 1 160 à 1 558 à 60 degrés de roulis. Plafond touché une seule fois, à 699 s, gaz à fond en Stabilize (pilote).

## 9 - Ce que le prochain vol doit contenir

1. Les paramètres ci-dessus chargés, vérifiés par deux comparaisons.
2. `INS_LOG_BAT_OPT` avec le bit post-filtre, `LOG_FILE_DSRMROT` à 1, `BATT_ARM_VOLT` à environ 43 V.
3. 30 à 40 s de hover calme à 5 m ou plus, en début de vol.
4. Coups de stick roll, pitch, yaw en AltHold, batteries pleines.
5. Montées et descentes franches en AltHold ; déplacements francs et arrêts nets en Loiter.
6. Surveiller : micro-oscillations et température moteur (passe-bas à 400 Hz), charge CPU, `RCOU` en yaw.
