# Glossaire de la formation 9

Les termes dans l'ordre où la formation les rencontre. Les mots anglais sont gardés quand c'est ce que les outils affichent.

**Target, desired** : la consigne, ce que le contrôleur doit atteindre. ArduPilot distingue parfois *desired* (ce que le pilote ou la navigation demande, brut) de *target* (la même chose après lissage et limitation par le contrôleur). Sur une courbe, c'est ce qu'on compare à *actual*.

**Actual** : la mesure, ce que les capteurs disent que le drone fait.

**Error** : l'écart entre target et actual.

**P, I, D** : les trois gains d'un contrôleur PID. P pousse proportionnellement à l'écart, I corrige l'écart qui persiste, D freine selon la vitesse de variation de l'écart. Voir 9.1, section 1.2.

**FF (feed-forward)** : une contribution qui anticipe la consigne à partir de sa pente, au lieu d'attendre l'écart. Réglé tard dans le processus, vers le troisième vol.

**Ratio P sur D** : la façon dont l'équipe raisonne un réglage de rate : monter le ratio rend le drone plus réactif (moins d'undershoot), le baisser plus amorti (moins d'overshoot). On préfère toujours bouger D vers le bas ou P vers le bas plutôt que monter D.

**Rate** : la vitesse angulaire, en degrés par seconde, autour d'un axe. Le contrôleur de rate est le plus bas de la chaîne d'attitude et le premier à régler.

**Angle** : l'inclinaison, en degrés. Le contrôleur d'angle commande le rate. Il n'a qu'un P.

**Roll, pitch, yaw** : rotation autour de l'axe avant-arrière (pencher à gauche ou à droite), autour de l'axe gauche-droite (piquer ou cabrer), autour de l'axe vertical (tourner sur place).

**Step response, réponse à l'échelon** : la courbe de la mesure quand la consigne saute brutalement. PID Review la normalise à 1.

**Undershoot** : la mesure n'atteint pas la consigne. **Overshoot** : elle la dépasse. **Amortissement critique** : elle arrive sur la consigne sans la dépasser, le plus vite possible.

**Latence, délai, retard de phase** : le temps entre la consigne et la réaction. Toujours présent en vol. Les filtres en ajoutent.

**Autorité** : la capacité des moteurs à produire l'effort demandé. Un drone qui manque d'autorité en yaw ne convergera jamais, quel que soit le gain.

**Marge de contrôle** : l'écart entre les sorties moteurs et leurs limites (`MOT_SPIN_MIN` en bas, 2 000 en haut). Sans marge, le contrôleur demande plus que les moteurs ne peuvent donner.

**Hover** : le vol stationnaire. `MOT_THST_HOVER` est la fraction de throttle qui le maintient.

**Sag** : la chute de voltage de la batterie quand le courant monte.

**Vibrations (VIBE)** : l'amplitude des accélérations que l'IMU subit, en m/s². **Clipping** : le nombre de fois où l'accéléromètre a dépassé sa plage de mesure.

**IMU** : l'unité inertielle, gyroscopes et accéléromètres. Les contrôleurs modernes en ont deux ou trois.

**Spectre** : l'amplitude des vibrations par fréquence. **dB (décibel)** : échelle logarithmique d'amplitude ; moins 20 dB veut dire une amplitude divisée par 10, moins 50 dB une vibration devenue négligeable.

**Harmonique** : une fréquence multiple de la fréquence fondamentale. Un moteur à 112 Hz excite aussi 224 et 336 Hz.

**Notch** : un filtre coupe-bande, qui atténue une bande étroite de fréquences. **Notch harmonique** : celui d'ArduPilot, centré sur la fréquence des moteurs et déplacé avec elle, avec ses harmoniques.

**Passe-bas** : un filtre qui laisse passer les basses fréquences et atténue les hautes. `INS_GYRO_FILTER` est celui du gyroscope.

**Bandwidth, bande passante d'un notch** : sa largeur. **Atténuation** : sa profondeur, en dB.

**Télémétrie ESC** : les données que les contrôleurs de moteurs renvoient (RPM, courant, température, voltage). Sur le Crash Proof, elles passent par le DShot bidirectionnel.

**Pôles** : le nombre d'aimants du moteur, dont l'ESC a besoin pour convertir sa mesure en RPM (`SERVO_BLH_POLES`).

**Loop rate** : la fréquence de la boucle principale de l'autopilote, 400 Hz par défaut. **DT** : le pas de temps entre deux passages du contrôleur, l'inverse du loop rate ; doit rester constant.

**EKF** : le filtre d'estimation d'état, qui fusionne IMU, GPS, baromètre et compas pour estimer position, vitesse et attitude.

**Glitch GPS** : une erreur momentanée du récepteur, qui croit s'être déplacé. Se voit par une chute de satellites et une hausse de `HAcc`.

**Rangefinder** : un capteur de distance au sol (lidar, ultrason). Ne dérive pas, contrairement au baromètre.

**Failsafe** : une action automatique déclenchée par une condition (batterie faible, perte radio). RTL : retour au point de départ. Land : atterrissage sur place.

**`.bin`, dataflash** : le log de l'autopilote, sur sa carte SD. **`.tlog`** : le log de télémétrie de Mission Planner.

**Journal d'hypothèses** : le tableau où l'on note, par vol et par contrôleur, l'observation, l'hypothèse chiffrée, ce qui a été appliqué et le résultat. Voir 9.4, section 6.
