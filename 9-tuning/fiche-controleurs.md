# Fiche des contrôleurs ArduCopter

Pour chaque étage de la chaîne : le mode de vol où il travaille, le message de log et les champs à comparer, les paramètres qui le règlent. Écrite pour **ArduCopter 4.6.3**, la version du Crash Proof. Certains noms changent en 4.7 ; la colonne est à compléter à la première lecture d'un log 4.7.

<!-- Cette fiche est une réécriture en markdown de la fiche HTML « controleurs-arducopter-4.6-4.7 » de la page Notion « Tuning guide ». À comparer avec l'original et à compléter pour 4.7. -->

Convention des champs : dans les messages `PSC*`, **D** en tête veut dire « desired » (demandé, brut), **T** « target » (après lissage et limitation), rien « actual ». Dans les messages `PID*`, `Tar` est la consigne et `Act` la mesure. Dans les noms de paramètres, `D` est la dérivée.

## 1 - Quels contrôleurs sont actifs dans quel mode

| Mode | Rate | Angle | Vitesse Z, accél. Z, position Z | Vitesse XY, position XY | Trajectoire |
|---|---|---|---|---|---|
| Acro | oui (consigne = stick) | non | non | non | non |
| Stabilize | oui | oui (consigne = stick) | non (throttle = stick) | non | non |
| AltHold | oui | oui | oui (vitesse Z = stick) | non | non |
| Loiter, PosHold | oui | oui | oui | oui (vitesse XY = stick, position tenue au relâché) | non |
| Guided | oui | oui | oui | oui | oui (cibles envoyées par le compagnon) |
| Auto | oui | oui | oui | oui | oui (waypoints) |
| RTL, Land | oui | oui | oui | oui | oui (interne) |

## 2 - Attitude

### Rate (vitesse angulaire)

| | Roll | Pitch | Yaw |
|---|---|---|---|
| Message et champs | `RATE.RDes` contre `RATE.R` ; `PIDR.Tar` contre `PIDR.Act` | `RATE.PDes` contre `RATE.P` ; `PIDP` | `RATE.YDes` contre `RATE.Y` ; `PIDY` |
| P, I, D | `ATC_RAT_RLL_P`, `_I`, `_D` | `ATC_RAT_PIT_P`, `_I`, `_D` | `ATC_RAT_YAW_P`, `_I`, `_D` (D à 0 : pas de D en yaw sauf moteurs inclinés) |
| Feed-forward | `ATC_RAT_RLL_FF` | `ATC_RAT_PIT_FF` | `ATC_RAT_YAW_FF` |
| Passe-bas internes | `ATC_RAT_RLL_FLTT` (consigne), `_FLTD` (dérivée), `_FLTE` (erreur) | idem `PIT` | idem `YAW` |
| Limites | `ATC_RAT_RLL_IMAX`, `_SMAX` | idem | idem |
| Crash Proof, 8 août | P 0,07, I 0,07, D 0,0018, FLTT et FLTD 21 Hz | idem | P 0,18 → 0,24, I 0,018, D 0 |
| Outil | PID Review (seul outil avec step response) | | |

Les champs `P`, `I`, `D`, `FF` des messages `PID*` donnent la contribution de chaque terme à la sortie : utile pour voir si c'est le D qui fait du bruit.

### Angle

| | Roll | Pitch | Yaw |
|---|---|---|---|
| Message et champs | `ATT.DesRoll` contre `ATT.Roll` | `ATT.DesPitch` contre `ATT.Pitch` | `ATT.DesYaw` contre `ATT.Yaw` |
| P (seul) | `ATC_ANG_RLL_P` | `ATC_ANG_PIT_P` | `ATC_ANG_YAW_P` |
| Crash Proof, 8 août | 4,5 → 4,05 | 4,5 → 4,05 | inchangé |
| Outil | UAV Log Viewer (mettre à l'échelle à la main) | | |

Paramètres d'agressivité liés à l'attitude : `ATC_ACCEL_R_MAX`, `ATC_ACCEL_P_MAX`, `ATC_ACCEL_Y_MAX` (accélérations angulaires max), `ATC_RATE_R_MAX`, `_P_MAX`, `_Y_MAX` (rates max, 0 = illimité), `ATC_INPUT_TC` (lissage du stick, 0,15 s par défaut), `ATC_SLEW_YAW`, `ANGLE_MAX` (inclinaison max, 30 degrés par défaut), et en Acro `ACRO_RP_RATE`, `ACRO_Y_RATE`.

## 3 - Chaîne verticale

| Étage | Message et champs | Paramètres | Notes |
|---|---|---|---|
| Position Z | `CTUN.DAlt` contre `CTUN.Alt` ; aussi `PSCD.TPD` contre `PSCD.PD` | `PSC_POSZ_P` (P seul) | Se règle en dernier de la chaîne verticale. |
| Vitesse Z | `CTUN.DCRt` contre `CTUN.CRt` ; aussi `PSCD.TVD` contre `PSCD.VD` | `PSC_VELZ_P`, `_I`, `_D`, `_FF`, `_FLTE`, `_FLTD`, `_IMAX` | À lire en AltHold. |
| Accélération Z | `PIDA.Tar` contre `PIDA.Act` ; aussi `PSCD.TAD` contre `PSCD.AD` | `PSC_ACCZ_P`, `_I`, `_D` (0), `_FF`, `_FLTT`, `_FLTD`, `_FLTE`, `_IMAX` | Commande directement le throttle. Crash Proof : P 0,015 → 0,15 (en vol, 8 août) → 0,18 (11 août) ; I 0,03 → 0,3. |

Autres champs utiles de `CTUN` : `ThI` (throttle demandé par le pilote), `ThO` (throttle envoyé), `ThH` (throttle de hover appris), `BAlt` (altitude baro), `SAlt` (rangefinder), `TAlt` (altitude terrain).

Agressivité verticale : `PILOT_SPEED_UP`, `PILOT_SPEED_DN`, `PILOT_ACCEL_Z` (ce que le stick peut demander), `PSC_JERK_Z`, `WPNAV_SPEED_UP`, `WPNAV_SPEED_DN`, `WPNAV_ACCEL_Z` (en mission).

## 4 - Chaîne horizontale

Un message par axe : `PSCN` (nord) et `PSCE` (est). Mêmes champs, N ou E en suffixe.

| Étage | Message et champs (nord) | Paramètres | Notes |
|---|---|---|---|
| Position XY | `PSCN.TPN` contre `PSCN.PN` (`DPN` = demandé brut) | `PSC_POSXY_P` (P seul) | |
| Vitesse XY | `PSCN.TVN` contre `PSCN.VN` (`DVN`) | `PSC_VELXY_P`, `_I`, `_D`, `_FF`, `_FLTE`, `_FLTD`, `_IMAX` | Il y a de l'inertie : PID complet. |
| Accélération XY | `PSCN.TAN` contre `PSCN.AN` (`DAN`) | pas de gains propres ; l'accélération demandée devient une consigne d'angle | La conversion accélération → angle passe par `PSC_ANGLE_MAX` (0 = `ANGLE_MAX`). |

Agressivité horizontale : `LOIT_SPEED`, `LOIT_ACC_MAX`, `LOIT_BRK_ACCEL`, `LOIT_BRK_JERK`, `LOIT_BRK_DELAY`, `LOIT_ANG_MAX` (Loiter au stick) ; `WPNAV_SPEED`, `WPNAV_ACCEL`, `WPNAV_JERK`, `WPNAV_RADIUS` (missions) ; `PSC_JERK_XY`.

## 5 - Moteurs et marge de contrôle

| Sujet | Message et champs | Paramètres |
|---|---|---|
| Sorties moteurs (PWM) | `RCOU.C1` à `C4` (jusqu'à `C8` en hexa ou octo) | `MOT_SPIN_ARM` (régime armé au sol), `MOT_SPIN_MIN` (plancher en vol), `MOT_SPIN_MAX`, `MOT_PWM_MIN`, `MOT_PWM_MAX` |
| Hover | `CTUN.ThH` ; événement à chaque désarmement | `MOT_THST_HOVER`, `MOT_HOVER_LEARN` (2 = apprend et sauvegarde), `MOT_THST_EXPO` |
| Compensation de voltage | | `MOT_BAT_VOLT_MAX`, `MOT_BAT_VOLT_MIN` |
| Priorité attitude contre throttle | | `ATC_THR_MIX_MIN`, `_MAN`, `_MAX` |
| Télémétrie ESC | `ESC[n].RPM`, `RawRPM`, `Volt`, `Curr`, `Temp` (`MotTemp` toujours 0) | `SERVO_BLH_POLES` (pôles moteur), `SERVO_BLH_TRATE`, `SERVO_BLH_AUTO` ; le RPM par DShot bidirectionnel demande un firmware `-bdshot` |

## 6 - Filtres

| Filtre | Paramètres | Notes |
|---|---|---|
| Passe-bas gyro | `INS_GYRO_FILTER` | 42 Hz sur le Crash Proof, à monter vers 400 (9.2). |
| Passe-bas accéléromètre | `INS_ACCEL_FILTER` | 20 Hz, on n'y touche pas. |
| Notch harmonique 1 | `INS_HNTCH_ENABLE`, `_MODE` (1 throttle, 3 télémétrie ESC, 4 FFT), `_FREQ`, `_BW`, `_ATT`, `_HMNCS` (bit 1 fondamentale, 2 deuxième, 4 troisième), `_REF` (= hover en mode throttle), `_OPTS` (bit 2 multi-source, 4 loop rate, 8 toutes les IMU), `_FM_RAT` | |
| Notch harmonique 2 | `INS_HNTC2_*` | Mêmes paramètres, un second notch, pour une résonance de châssis par exemple. |
| FFT en direct | `FFT_ENABLE` et `FFT_*` | Seulement en dernier recours. |
| Journalisation pour Filter Review | `INS_LOG_BAT_MASK` (IMU à enregistrer), `INS_LOG_BAT_OPT` (bit 1 post-filtre, bit 2 pré et post), `INS_LOG_BAT_CNT`, `INS_LOG_BAT_LGIN`, `INS_LOG_BAT_LGCT` | |
| Passe-bas internes des PID | `*_FLTT`, `*_FLTD`, `*_FLTE` de chaque contrôleur | Filtres sur la consigne, la dérivée et l'erreur de chaque PID ; à baisser si un contrôleur vibre autour de sa consigne. |

## 7 - Messages de santé et de contexte

| Sujet | Message et champs | Seuils ou usage |
|---|---|---|
| Vibrations | `VIBE.VibeX`, `VibeY`, `VibeZ` (m/s²), `Clip` (compteur), une instance par IMU | Moyenne sous 15, pic sous 30 hors impact ; clip localisé et expliqué |
| Performance | `PM.LR` (loop rate), `Load` (en dixièmes de pour cent : 268 = 26,8 %), `Mem`, `NLon` (boucles longues), `MaxT` | LR stable, Load sous 50 %, Mem jamais 0 |
| Alimentation du contrôleur | `POWR.Vcc`, `VServo`, `Flags` | Vcc stable, jamais sous 3,1 V |
| Batterie | `BAT.Volt`, `VoltR` (au repos, compensé du sag), `Curr`, `CurrTot`, `Res` (résistance interne estimée) | Sag = `Volt` en charge contre `VoltR` |
| Failsafes batterie | | `BATT_ARM_VOLT` (> `BATT_LOW_VOLT` + sag), `BATT_LOW_VOLT`, `BATT_FS_LOW_ACT` (2 RTL), `BATT_CRT_VOLT`, `BATT_FS_CRT_ACT` (1 Land), `BATT_LOW_TIMER`, `BATT_FS_VOLTSRC` |
| Autres failsafes | `EV` et `MSG` quand ils se déclenchent | `FS_THR_ENABLE`, `FS_GCS_ENABLE`, `FS_EKF_ACTION`, `FS_EKF_THRESH`, `FENCE_ENABLE`, `FENCE_TYPE`, `FENCE_ACTION`, `RTL_ALT` |
| GPS | `GPS.NSats`, `HDop`, `Alt` (niveau de la mer), `Spd` (vitesse sol) ; `GPA.HAcc`, `VAcc`, `SAcc` (précisions) | Glitch = chute de `NSats` avec hausse de `HAcc` ; `EK3_GLITCH_RAD`, `GPS_HDOP_GOOD` |
| Altitudes | `CTUN.Alt` (EKF, relatif au décollage), `BARO.Alt`, `GPS.Alt`, `RFND.Dist`, `POS.RelHomeAlt` | Repères différents : toujours demander lequel |
| Entrées pilote | `RCIN.C1` à `C16` (1 000 à 2 000, centre 1 500) | Mapping à connaître : sur le Crash Proof `C1` roll, `C2` pitch, `C3` gaz, `C4` yaw |
| Événements | `EV.Id` (10 armé, 11 désarmé, autres : voir la liste ArduPilot), `MODE.Mode`, `MSG.Message` | Datent le vol |
| Paramètres | `PARM.Name`, `Value` ; réémis à chaque changement en vol | Découper le log aux changements |
| Températures | `POWR` ou `MCU` selon la carte (contrôleur), `IMU.T` (IMU), `ESC.Temp` | À surveiller, pas de seuil dur |

## 8 - Journalisation

| Paramètre | Rôle |
|---|---|
| `LOG_BITMASK` | Quels messages sont enregistrés. Pour le tuning : Fast Attitude (bit 0), PID (bit 12), IMU Fast (bit 18). |
| `LOG_DISARMED` | Enregistrer aussi désarmé (utile pour un problème au sol, sinon 0). |
| `LOG_FILE_DSRMROT` | 1 = nouveau fichier à chaque désarmement. |
| `LOG_FILE_BUFSIZE` | Tampon d'écriture ; à monter si des messages sont perdus. |

<!-- Colonne 4.7 : à compléter. Les paramètres PSC_* et les messages PSC* ont été partiellement renommés dans les versions récentes ; vérifier sur le premier log 4.7 de l'équipe. -->
