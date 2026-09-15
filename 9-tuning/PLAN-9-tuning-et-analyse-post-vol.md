# Plan de la formation 9 : tuning et analyse post-vol

*Document de travail, 15 septembre 2026. Ce n'est pas la formation : c'est sa structure, le contenu à y mettre, et les questions à trancher avant la rédaction. Source principale : la séance donnée à Tom le 11 août 2026 (2 h 16, log du premier vol du Crash Proof), complétée par la page Notion « Tuning guide » et ses sous-pages, et par le plan d'apprentissage (bloc B9, objectif 6, jalon du 24 octobre).*

*Le numéro est provisoire. Le plan d'apprentissage place cette formation en B9, branche parallèle à partir de B3 ; Colin la nommait « B5 ou B6 » de mémoire. Voir la question 1.*

---

## 0. Ce que la formation doit accomplir

### Le public

Une recrue qui a fait les formations 0 à 1 (Mission Planner, paramètres, simulation), qui n'a pas nécessairement suivi un cours d'asservissement, et qui n'a peut-être jamais touché à ArduPilot au-delà de l'interface. Elle sera un jour seule devant un log de premier vol, avec un pilote qui attend une réponse à « on change quoi ? ».

Ce que Tom a demandé au début de la séance résume bien le besoin : « avoir une bonne vue d'ensemble pour que je puisse bien deviner les trucs à corriger ».

### Le résultat attendu

À la fin, la recrue est capable de :

- Ouvrir le log d'un premier vol dans les trois outils web d'ArduPilot et savoir lequel sert à quoi.
- Vérifier que le drone et les données sont sains avant de conclure quoi que ce soit (vibrations, loop rate, RPM, voltage, CPU).
- Lire une réponse rate ou angle (target contre actual, step response) et dire : undershoot, overshoot ou correct.
- Traduire cette lecture en un changement de paramètre, dans le bon sens, avec un ordre de grandeur, et savoir pourquoi on touche D en dernier.
- Placer un notch harmonique et un passe-bas à partir du Filter Review, avec la cible de moins 50 dB et le réflexe « le moins de filtres possible ».
- Tenir un journal d'hypothèses par vol et itérer sur 3 à 10 vols dans le bon ordre (filtres, rates, angle, vitesse, position, puis agressivité).
- Se servir des logs pour reconstruire ce qui s'est passé pendant un vol qui a mal tourné (entrées pilote, moteurs, altitude, GPS).

### Le fil conducteur

**Un seul log réel, suivi du début à la fin.** Le log du premier vol du Crash Proof (11 août 2026) contient tout : un hover calme pour les filtres, des coups de stick roll, pitch et yaw pour les rates, un épisode AltHold problématique, un rebond à l'atterrissage qui fait clipper l'IMU, un glitch GPS, un sag de batterie. La formation reproduit l'analyse faite en séance, dans l'ordre logique (pas dans l'ordre de la séance, voir la question 4), et arrive aux mêmes conclusions que la page « Notes CP » du 11 août : yaw rate P plus 30 %, angle roll et pitch P moins 10 %, PSC_ACCZ_P plus 20 %, notch recentré à 111-112 Hz, passe-bas à 400 Hz.

Le défi final utilise un **deuxième log** que la recrue analyse seule (voir la question 6).

### Ce qui distingue cette formation des autres

Les formations 1 à 3 construisent quelque chose (un script, un conteneur, une node) et la réussite se voit à l'écran. Ici, il n'y a rien à construire : c'est une formation de lecture et de jugement. Le risque est que la recrue lise passivement. D'où les choix ci-dessous :

- Chaque section se termine par une question « toi, tu vois quoi ? » avant la réponse, comme Colin l'a fait avec Tom tout au long de la séance (« Qu'est-ce que tu pourrais dire de ça, Tom ? »). La réponse est masquée dans un bloc `<details>`.
- Chaque section demande de reproduire une capture précise sur le log fourni (le même graphique que celui de la formation, refait par la recrue).
- Le défi final est un vrai livrable : un journal d'hypothèses sur un log inconnu, posté sur Discord, que Colin ou un directeur commente. C'est exactement ce qui a été demandé à Tom en fin de séance (« texte-moi tes interprétations, je vais te donner la mienne »).

---

## 1. Découpage proposé

Quatre documents, comme la formation 3, pour que chacun ait une réussite claire et une durée sous deux heures. Durées estimées pour la recrue, lecture et exercices compris ; à mesurer sur la première cohorte.

| Document | Sujet | Réussite | Durée estimée |
|---|---|---|---|
| 9.1 Lire un log | Fichiers, outils, chaîne de contrôleurs, santé du système | La recrue a ouvert le log dans les trois outils et rempli la fiche de santé | 1 h 30 |
| 9.2 Vibrations et filtres | Filter Review, notch harmonique, passe-bas, VIBE et clipping | La recrue a produit un fichier de paramètres de filtre qui laisse les pics juste sous moins 50 dB | 1 h 30 |
| 9.3 Les rates | PID Review, step response, ratio P/D, le cas du yaw | La recrue a noté trois hypothèses chiffrées (roll, pitch, yaw) et elles correspondent aux Notes CP | 1 h 30 |
| 9.4 Le reste de la chaîne et la démarche | Angle, vertical, horizontal dans UAV Log Viewer ; journal d'hypothèses ; agressivité ; lire un vol raté | Défi : journal complet sur le deuxième log | 2 h |

Total : environ 6 h 30 pour la recrue. Le plan d'apprentissage budgète 8 h de rédaction pour l'objectif 6 (6 h initiales plus 2 h d'analyse post-vol), ce qui est serré pour quatre documents ; voir la question 2.

Un annexe transversal : **la fiche des contrôleurs** (voir section 7 et la question 8).

---

## 2. Document 9.1 : lire un log

### Objectifs

- Distinguer le `.bin` (dataflash, sur la carte SD du drone) du `.tlog` (télémétrie, enregistré par Mission Planner), et savoir lequel ouvrir pour quoi.
- Ouvrir un log dans UAV Log Viewer, PID Review et Filter Review, et savoir ce que chacun fait de mieux.
- Situer les six contrôleurs de la chaîne ArduCopter et savoir lequel est actif dans quel mode de vol.
- Passer la liste de vérifications de santé avant toute analyse de tuning.

### Bloc « Avant de commencer »

- Durée : 1 h 30.
- Prérequis : formation 1 faite (Mission Planner, onglet Config, gestion des paramètres). Aucun cours d'asservissement requis.
- À la fin : la fiche de santé du log du Crash Proof remplie.
- Aide : Discord, salon Contrôle, fil « Formations et Questions ».
- À poster à la fin : la fiche de santé remplie.
- Matériel : le log `.bin` du premier vol du Crash Proof (11 août 2026), fourni dans le dossier de la formation ou par lien (voir la question 6 sur la taille).

### 1. Deux fichiers par vol

- Le `.bin` : tout ce que l'autopilote a mesuré et calculé, plusieurs centaines de fois par seconde. C'est le fichier qu'on analyse.
- Le `.tlog` : ce que Mission Planner a vu passer, dont les messages jaunes et rouges. Sert à rejouer l'interface et à relire un avertissement. Peu d'information pour le tuning.
- Où les trouver : carte SD via Mission Planner (Download DataFlash Log), dossier `logs` de Mission Planner pour les tlogs.
- La taille : au-delà de 300 à 400 Mo, les outils web ne chargent plus. Deux parades : déconnecter et reconnecter le drone entre les vols pour découper les logs, ou découper après coup (outil à nommer, Colin n'en a pas parlé en séance ; voir la question 9).
- Ce qui doit être activé avant le vol pour que le log serve au tuning (la page Notion « Tuning 1er → 2 vol » le liste) : fast rate logging (courbes d'angle et de rate lisses), RPM moteur qui fait du sens (télémétrie ESC branchée, nombre de pôles correct), données IMU batch pour la FFT (`INS_LOG_BAT_MASK`), et si on veut voir le post-filtre réel, l'option batch post-filtre (`INS_LOG_BAT_OPT`), que Colin n'avait pas activée le 11 août. À placer ici ou dans une section « préparer un vol de tuning » (question 3).

### 2. Les trois outils

Tableau de choix :

| Outil | Pour quoi | Ne pas l'utiliser pour |
|---|---|---|
| [PID Review](https://firmware.ardupilot.org/Tools/WebTools/PIDReview/) | Les rates uniquement : time domain target contre actual, step response, historique des gains changés en vol | Les autres contrôleurs (buggy, courbes manquantes) ; l'onglet output |
| [Filter Review](https://firmware.ardupilot.org/Tools/WebTools/FilterReview/) | Vibrations en dB, placement des notches et du passe-bas, phase, export des paramètres | Le tuning des PID |
| [UAV Log Viewer](https://plot.ardupilot.org/) | Tout le reste : tout tracer contre tout, événements, paramètres, VIBE, RCIN, RCOU, ESC, GPS, altitudes | Les step responses (il n'en calcule pas) |
| [Hardware Report](https://firmware.ardupilot.org/Tools/WebTools/) (dans la suite WebTools) | Santé du système en une page : calibrations, températures, voltage FC, CPU, loop rate, budgets série, messages perdus | |

Point de méthode : UAV Log Viewer oblige à mettre les courbes à l'échelle soi-même, ce qui est pénible et parfois trompeur ; c'est pour ça que les rates se lisent dans PID Review.

### 3. La chaîne de contrôleurs

Le schéma (celui de la page Notion, généré avec Claude, à revérifier avant publication) : trajectoire (modes Guided, Auto) → position → vitesse → accélération et angle → rate → mix moteur → moteurs, et en parallèle la chaîne verticale : trajectoire Z → position Z → vitesse Z → accélération Z.

Deux idées à faire passer ici, avant toute mécanique :

- **Chaque contrôleur commande le suivant.** Si le rate est mal réglé, tout ce qui est au-dessus a l'air mal réglé. On règle donc de bas en haut : rate d'abord, puis angle, puis vitesse, puis position. Un contrôleur d'angle qui « traîne » alors que le rate manque de P, c'est normal, on ne touche pas l'angle.
- **Le mode de vol détermine quels contrôleurs sont actifs.** Stabilize : angle et rate seulement, le pilote fait le reste. AltHold : plus la chaîne verticale. Loiter, Guided, Auto : toute la chaîne. Donc pour régler les contrôleurs verticaux, il faut voler en AltHold ; pour la position, en Loiter ou Guided. C'est la table « modes de vol et contrôleurs actifs » de la fiche des contrôleurs.

Vocabulaire à fixer, une fois pour toutes, ici : target ou desired (la consigne), actual (la mesure), error, gains P, I, D, FF. Une explication de dix lignes de ce que font P, I et D, sans équation, avec l'image du drone qui doit atteindre un angle : P pousse proportionnellement à l'écart, D freine proportionnellement à la vitesse à laquelle l'écart change, I corrige l'écart qui reste. Voir la question 5 sur la profondeur de ce primer.

### 4. La fiche de santé

La liste de la sous-page Notion « Vérifications », dans l'ordre de la séance, avec pour chacun : où le lire, la valeur mesurée sur le Crash Proof, le seuil, et quoi faire si ce n'est pas bon.

| Vérification | Où | Crash Proof 11 août | Seuil ou attendu |
|---|---|---|---|
| Vibrations absolues (VIBE X, Y, Z) | UAV Log Viewer | 1 à 2 m/s² en moyenne, 5 en pic ; Z domine | Moyenne sous 15 m/s² ; pic sous 30 m/s² (3 G) ; au-dessus de 60 m/s² (6 G) le drone se désintègre |
| Clipping (VIBE Clip0, 1, 2) | UAV Log Viewer | 75 au total, par paliers, pendant les vols AltHold et au rebond d'atterrissage | Le moins possible ; localisé et explicable, c'est tolérable ; croissant pendant un vol calme, c'est mécanique |
| Loop rate (PM) | Hardware Report | Pire cas 382 Hz pour une boucle à 400 | Stable ; un écart de 50 à 100 Hz casse le DT des PID |
| Charge CPU (PM Load) | Hardware Report | 30 % | Jamais au-dessus de 50 %, pour encaisser les pics ; chaque notch ajouté augmente la charge |
| Mémoire libre | Hardware Report | OK | Jamais zéro |
| Voltage du FC (POWR Vcc) | Hardware Report, UAV Log Viewer | 3,27 V constant | Stable ; des chutes sous 3,1 V sont graves |
| Température MCU | UAV Log Viewer | jusqu'à 65 °C | À surveiller ; ventilation |
| Messages perdus (dropped) | Hardware Report | 0 | 0 ; sinon la carte SD ne suit pas et il manque des morceaux de log |
| Budgets des ports série | Hardware Report | Tous sous la limite ; RCIN un peu plus près | Sous la capacité (115 200 bauds = 115 200 octets/s au maximum, à vérifier) |
| Télémétrie ESC présente (ESC RPM, Curr, Temp, Volt) | UAV Log Viewer | Présente, RPM 6 600 à 6 700 en hover, 45 °C | Présente et cohérente : RPM = fréquence du pic moteur × 60 (112 Hz × 60 = 6 720, cohérent) |
| Nombre de pôles (SERVO_BLH_POLES) | Paramètres | Correct | Si le RPM est un multiple entier de la valeur attendue d'après la fiche moteur, le nombre de pôles est faux ; à corriger avant tout tuning de filtre |
| Calibrations (température, compas, compas-moteurs, baro-vent) | Hardware Report | Compas OK ; pas de calibration température ni compas-moteurs | Mineur ; à faire sur le prochain drone (nuit au congélateur pour la température) |
| Positions des capteurs | Hardware Report | IMU 1 et 2 superposées, GPS devant | Visuellement cohérent avec le drone |
| Paramètres changés en vol | Hardware Report, PID Review | Liste des gains changés et à quel moment | Sert à retrouver quel réglage était actif à quel moment |
| Dérive d'horloge GPS | Hardware Report | 7 s sur le vol | Sans conséquence |
| Sag de la batterie | UAV Log Viewer, BAT Volt | 0,5 V au décollage, 0,7 à 0,8 V près du low voltage, jusqu'à 2 V sur les coups de gaz | BATT_ARM_VOLT doit dépasser BATT_LOW_VOLT d'au moins le sag, viser 1 à 1,2 V ; mesurer le sag en fin de vol, près du low voltage |
| Courant batterie | BAT Curr | Incohérent (paramètres du moniteur non activés) | Si absent, le courant ESC dépanne |
| Hover appris (événement MOT_THST_HOVER) | UAV Log Viewer, événements | 0,125, le plancher | Laisser apprendre (MOT_HOVER_LEARN) ; 0,125 veut dire un rapport poussée/poids supérieur à 8 |

Exercice : remplir cette fiche sur le log fourni. Chaque ligne est une capture à refaire. C'est long mais c'est l'exercice qui rend la recrue autonome : après ça, elle sait naviguer dans les trois outils.

> Tu as réussi si : la fiche est remplie, et tu sais dire pour chaque ligne si le Crash Proof était sain le 11 août (réponse : oui sur toute la ligne).

### Images à fournir (Colin)

- Onglet de téléchargement des logs dans Mission Planner.
- Écran d'ouverture de chacun des trois outils avec le log chargé.
- Le schéma de la chaîne de contrôleurs, revu.
- Le Hardware Report du Crash Proof, section par section (loop rate, CPU, voltage, série, dropped).
- VIBE et Clip dans UAV Log Viewer, avec l'altitude superposée pour montrer le rebond d'atterrissage.
- ESC RPM contre RCOU du même moteur, superposés (même forme).
- BAT Volt avec les deux mesures de sag annotées.

---

## 3. Document 9.2 : vibrations et filtres

### Objectifs

- Comprendre pourquoi on filtre, et pourquoi on filtre le moins possible.
- Choisir la bonne portion de vol et lire le spectre pré-filtre.
- Configurer le notch harmonique (mode, source, multisource, loop rate, IMU, fréquence, bandwidth, atténuation, harmoniques) et le passe-bas gyro.
- Exporter, importer et vérifier les paramètres.

### Bloc « Avant de commencer »

- Durée : 1 h 30.
- Prérequis : 9.1 (le RPM est vérifié, sinon tout ce qui suit est faux).
- À la fin : un fichier de paramètres de filtre exporté depuis Filter Review, qui laisse tous les pics juste sous moins 50 dB avec le moins de filtres possible.
- À poster : la capture « estimated post-filter » finale et le fichier de paramètres.

### 1. Pourquoi filtrer, et pourquoi pas trop

Les trois phrases de la séance, à mettre en encadré, parce que c'est ce que la recrue doit retenir si elle ne retient qu'une chose :

- Les moteurs font vibrer l'IMU à leur fréquence de rotation et ses harmoniques. Sans filtre, le PID réagit à ces vibrations comme si le drone bougeait : moteurs qui chauffent, micro-oscillations, bruit.
- **Chaque filtre ajoute du retard** (délai de phase). Trop filtrer, c'est un drone qui réagit en retard, donc un PID qui a l'air mal réglé alors que c'est le filtre. Le 11 août, le Crash Proof était filtré à moins 70 et moins 90 dB, avec environ 200 degrés de retard de phase.
- **La cible est moins 50 dB, pas moins.** Sous moins 50 dB, une vibration n'existe pratiquement plus (l'écart entre moins 50 et moins 60 change la vibration d'une fraction de pour cent). Descendre plus bas n'apporte rien et coûte du retard. Valeur documentée, utilisée par les développeurs d'ArduPilot.

Une explication courte du décibel (échelle logarithmique, moins 3 dB = moitié de puissance, moins 20 dB = amplitude divisée par 10) pour que « moins 50 » veuille dire quelque chose. Voir la question 5.

### 2. La portion de vol à analyser

- Un hover calme, sans commandes, de 20 à 30 secondes au moins. Throttle constant, roll et pitch quasi nuls. Pourquoi : on ne veut pas que les corrections des PID contaminent le spectre.
- Pourquoi le hover plutôt que le plein gaz : le tuning des filtres se centre sur la fréquence en hover, puis le notch suit le RPM. Et Zenith passe l'essentiel de ses vols en hover : c'est là que le contrôle de vibration compte. Un FPV ferait autrement.
- Conséquence sur la routine de vol : décoller, ne rien faire pendant 30 à 40 secondes, puis faire les coups de stick pour les rates, puis le reste. Tous les tests de vol de tuning commencent comme ça.

### 3. Lire le spectre pré-filtre

Sur le Crash Proof : un gros pic vers 114 Hz (la fréquence moteur en hover, 6 700 tr/min divisés par 60), un autre vers 350 (harmonique), des petits pics à des fréquences quelconques (fils, tie-wraps, antennes qui résonnent), quelque chose vers 30 Hz, et une bosse plus large qui est probablement la résonance de la structure.

Ce qu'on traite : les pics au-dessus de moins 50 dB. Le reste, on l'oublie.

Question à la recrue avant la réponse : « en dessous de 700 Hz, tu vois quoi ? » (Tom : un gros pic vers 111-113, un autre vers 350.)

### 4. Le notch harmonique

Séquence exacte de la séance, à reproduire pas à pas dans Filter Review :

1. **Mode** (`INS_HNTCH_MODE`) : fixe (jamais), throttle (premier vol seulement, parce qu'on ne sait rien ; objectivement mauvais puisque 50 % de gaz en plus ne fait pas tourner les moteurs 50 % plus vite), capteur RPM externe (non), **télémétrie ESC** (ce qu'on veut : le notch suit la vraie fréquence de chaque moteur), FFT en direct (seulement si on n'arrive pas à gérer les vibrations autrement : charge CPU et délai).
2. **Options** (`INS_HNTCH_OPTS`) : multisource (un notch par moteur au lieu d'une moyenne : 4 sur Crash Proof, 6 sur EXA), update at loop rate (le notch se recale à chaque boucle PID, 400 Hz), enable on all IMUs. Le coût : 4 moteurs × 3 IMU × harmoniques cochées = 12, 24 notches. Un H7 encaisse, un F4 non. C'est pour ça qu'on surveille la charge CPU.
3. **Fréquence** (`INS_HNTCH_FREQ`) : la valeur en hover lue sur le spectre, 114 Hz, puis recentrée à 111-112 après recalcul parce que le pic n'était pas tout à fait là où le calcul l'annonçait. Le premier réglage (102 Hz, calculé d'après la fiche des moteurs) était à côté du pic : les moteurs tournent plus vite que la fiche.
4. **Bandwidth** (`INS_HNTCH_BW`) : la doc conseille au moins un quart de la fréquence ; ramené de très large à 10, puis 12.
5. **Atténuation** (`INS_HNTCH_ATT`) : ramenée à 5 dB. On réduit jusqu'à ce que le pic soit juste sous moins 50.
6. **Harmoniques** (`INS_HNTCH_HMNCS`) : garder celles qui remontent au-dessus de moins 50 sans elles. Le 11 août, sans la troisième harmonique un pic remonte à moins 43 dB, donc on la garde. La logique cible : une fondamentale plus l'harmonique qui correspond au nombre de pales, une seule notch bien placée.
7. **Recalculate**, à chaque changement, en affichant « estimated post-filter » (le post-filtre réel n'est disponible que si l'option batch post-filtre était activée en vol).

Deux détails de la séance à garder parce qu'ils enseignent la méthode :

- Filter Review affichait le notch précédent à 106 Hz alors que le paramètre disait 102 : question ouverte le 11 août, à résoudre avant publication (question 9).
- « Un peu à droite, je décale à gauche et j'élargis » : le placement se fait à l'œil, en recalculant. C'est du gossage assumé.

### 5. Le passe-bas gyro

`INS_GYRO_FILTER` était à 42 Hz (valeur par défaut) et lavait tout ce qui est au-dessus, d'où le sur-filtrage. Remonté à 400 Hz : la boucle gyro est à 400 Hz, il ne sert plus qu'à dégrader doucement les petites vibrations hautes fréquences. Colin le qualifie lui-même d'agressif, à surveiller au vol suivant (micro-oscillations des PID ? alors redescendre).

Ce que montre l'expérience à 800 Hz faite en séance : le passe-bas quasi désactivé fait ressortir un petit pic qu'on préfère couper, et le retard de phase à 800 Hz ne veut rien dire (une demi-milliseconde).

### 6. La phase

À traiter honnêtement : Colin dit en séance avoir lui-même de la difficulté à juger quelles valeurs de phase sont acceptables. La règle pratique : la phase seule ne dit rien tant qu'on ne la rapporte pas à la fréquence de coupure du système ; si le drone est instable et que tous les PID ont l'air bons, c'est probablement là que ça se passe. Pour cette formation, la lecture reste comparative : avant 200 degrés, après 50 à 60, on a gagné.

### 7. Exporter, importer, vérifier

- Save parameters dans Filter Review, nommer le fichier (drone, date, vol).
- Importer dans Mission Planner (onglet Config, Full Parameter List, Load from file).
- **Comparer deux fois** : la première comparaison peut ne pas tout appliquer si l'enable n'était pas actif ; on recompare pour être sûr que rien n'a été oublié. C'est l'action donnée à Téva en séance.

### 8. Après le vol suivant

Le filtrage se refait à chaque changement mécanique ou de charge utile, et se revérifie sur 3 à 10 vols avec les PID. Ce n'est pas une opération unique.

> Tu as réussi si : ton estimated post-filter a tous ses pics sous moins 50 dB, avec une seule notch (plus harmoniques) et un passe-bas à 400 Hz, et le fichier exporté contient les mêmes valeurs que les Notes CP.

### Images à fournir

- Filter Review : sélection de la zone calme, spectre pré-filtre annoté (114, 350, petits pics).
- Le post-filtre du 11 août tel qu'il était (moins 70, moins 90 dB) contre le pré-filtre.
- Le menu de configuration du notch avec chaque champ.
- Trois recalculs successifs (trop atténué, presque, bon).
- Le spectrogramme avec les notches qui suivent le RPM (zone grise des quatre notches).
- Le graphe de phase avant et après.
- Save parameters, puis la comparaison dans Mission Planner.

---

## 4. Document 9.3 : les rates

### Objectifs

- Sélectionner la bonne portion de vol et calculer une réponse dans PID Review.
- Lire target contre actual et la step response ; nommer undershoot, overshoot, correct.
- Décider quel gain bouger, dans quel sens, de combien.
- Comprendre pourquoi le yaw est différent (pas de D, manque d'autorité) et pourquoi les gros drones sont difficiles en yaw.

### Bloc « Avant de commencer »

- Durée : 1 h 30.
- Prérequis : 9.1 et 9.2. Les filtres passent avant les rates parce qu'un rate qui a l'air mal réglé est souvent un filtre en retard.
- À la fin : trois hypothèses chiffrées (roll, pitch, yaw) notées dans ton journal.
- À poster : les trois step responses et tes trois hypothèses.

### 1. La routine de vol pour les rates

- Après le hover calme : coups de stick francs d'un côté puis de l'autre, en roll, puis en pitch, puis en yaw. Le but est de ressembler à un échelon.
- Ce qu'il faut dire au pilote : bouger le stick d'un côté à l'autre, pas le lâcher pour qu'il vibre comme un ressort (ça fausse les données).
- **Batteries pleines.** Le tuning se fait en début de vol, parce que le voltage donne la poussée, donc l'autorité. Ce qu'on mesure en fin de vol sous-estime ce que le drone peut faire. Le 11 août, les coups de stick ont été faits plus tard dans le vol ; Colin en tire des hypothèses mais refuse de les appliquer sans les refaire en début de vol.
- La vitesse du coup de stick dépend du véhicule : moins vite sur EXA que sur Crash Proof.

### 2. Sélectionner et calculer

- Ne jamais analyser une zone au sol ou quasi au sol : ça donne n'importe quoi et on conclut à tort que c'est mal réglé.
- Sélectionner la zone des coups de stick, cliquer Calculate. Idéalement une zone par axe.
- PID Review ne sert qu'aux rates (le reste est buggy ou pas logué par défaut ; PIDR et compagnie sont pour d'autres véhicules). L'onglet output ne sert à rien.

### 3. Lire la réponse

**Time domain.** La target est le mapping du stick, l'actual la mesure. On compare les sommets. Roll : 234 contre 229, quasiment identique, « presque un tuning parfait ». Pitch : 228 contre 221, léger undershoot. Yaw : 146 commandé, 121 atteint, net undershoot.

**Step response.** L'outil normalise chaque commande à 1 et superpose les réponses. Ligne bleue = moyenne, c'est elle qu'on lit ; les lignes qui divergent sont des artefacts numériques (des commandes minuscules, 0,001 degré, qu'on n'atteint jamais, sans importance).

- Idéal : une montée franche, un petit overshoot, puis stabilisation. Pour les gros drones, Colin préfère l'amortissement critique : se poser sur la ligne sans dépasser.
- Une deuxième oscillation sous la ligne : pas idéal, mais pas un problème tant qu'elle est petite. Il y a une plage acceptable.
- Une réponse lente qui n'atteint jamais 1 (yaw à 0,75-0,80) : pas assez de gain ou pas assez d'autorité. La commande demande 150 degrés par seconde, le drone en fait 125.

**La latence est toujours là.** À l'école (asservissement), l'entrée est instantanée. En vol, elle ne l'est jamais : on bouge un stick. Il y a toujours un retard entre target et actual. Le seul moyen de le réduire est de monter les gains, donc l'agressivité, avec les risques qui viennent avec. Le feed-forward (`ATC_RAT_*_FF`) anticipe la pente de la commande et vient « coller » la courbe ; on ne le touche qu'au troisième vol environ, une fois les PID satisfaisants.

**Spectrogramme.** La ligne bleue à 110-114 Hz, c'est le PID endormi par le notch : il ne réagit pas à la fréquence moteur, ce qui est voulu. Le problème serait un notch posé sur une résonance de structure à 40 Hz : le PID ne corrigerait plus rien à cette fréquence-là. C'est le lien avec 9.2.

Questions à la recrue avant chaque réponse : « en pitch, tu vois quoi ? » (un peu en dessous des sommets), « en yaw ? » (undershoot), « on monte quoi ? ».

### 4. Décider du changement

La règle en trois temps :

1. **Undershoot : monter le ratio P/D. Overshoot : le baisser.**
2. **Bouger D vers le bas de préférence, sinon P.** Pour monter le ratio : baisser D. Pour le baisser : baisser P, pas monter D. D fait chauffer les moteurs et injecte du bruit ; on garde toujours le D le plus petit qui stabilise le système. On ne monte D qu'en dernier recours.
3. **L'ordre de grandeur : le ratio des sommets, supposé linéaire, puis arrondi vers le haut** parce que ce n'est pas linéaire. Pitch : 228/221, environ 0,5 %, jugé trop petit pour être significatif, on monte de 3 à 5 %. Yaw : 146/121, environ 20 %, on vise 30 % d'expérience (« j'ai de la misère à justifier pourquoi 30 et pas 20 » : Colin le dit, la formation le dit aussi). Un changement trop petit n'est pas dangereux, on converge sur plusieurs vols.

Roll et pitch : on suppose les mêmes gains au départ si le drone est à peu près symétrique, puis on les sépare, parce que la batterie place plus d'inertie sur un axe que sur l'autre.

### 5. Le cas du yaw

- **Pas de D en yaw** (`ATC_RAT_YAW_D` à 0). Le drone tourne par transfert de moment entre les moteurs qui accélèrent dans un sens et ceux qui décélèrent dans l'autre ; l'amortissement aérodynamique et l'inertie des moteurs jouent le rôle du D. Il reste un P, et le ratio P/D revient à monter P.
- **Le yaw est le mouvement le plus exigeant** : c'est celui où les moteurs s'écartent le plus les uns des autres (visible dans RCOU). Les gros drones manquent d'autorité en yaw et undershootent systématiquement ; certains ne convergent jamais.
- La parade mécanique : incliner les moteurs (EXA, 3 degrés avant et arrière en sens opposés) pour ajouter une composante de poussée qui aide la rotation. 3 degrés n'ont pas suffi ; le prochain drone aura des trous pour 5 degrés. Un drone à moteurs inclinés a besoin d'un D en yaw, parce qu'il y a alors une vraie accélération à freiner.

### 6. Changer les gains en vol

PID Review montre l'historique des gains actifs pendant le vol. On peut donc essayer une dizaine de valeurs dans un même vol et converger vite sur un drone mal réglé. Comment on fait en pratique (Mission Planner, onglet Config, Extended Tuning ou un canal de tuning radio ?) : à préciser, Colin ne l'a pas montré (question 9).

> Tu as réussi si : tes trois hypothèses sont « roll : rien », « pitch : P/D plus 3 à 5 % via D », « yaw : P plus 30 % », et tu sais expliquer pourquoi on ne monte pas D.

### Images à fournir

- PID Review : sélection des coups de stick sur la vue d'ensemble.
- Time domain roll, pitch, yaw, zoomés sur un sommet avec les valeurs.
- Step response roll (bonne), pitch (un peu sous la ligne), yaw (0,75, jamais 1).
- Spectrogramme avec la ligne bleue à 110 Hz.
- L'historique des paramètres changés en vol.
- RCOU pendant les coups de stick roll, pitch, puis yaw, pour montrer que le yaw écarte les moteurs.

---

## 5. Document 9.4 : le reste de la chaîne et la démarche

### Objectifs

- Reproduire dans UAV Log Viewer le graphique target contre actual pour l'angle, le vertical et l'horizontal, et savoir quels messages et quels paramètres correspondent (la fiche des contrôleurs).
- Vérifier la marge de contrôle des moteurs avant de monter des gains.
- Tenir le journal d'hypothèses et connaître l'ordre des vols.
- Reconstruire un vol qui a mal tourné à partir de RCIN, RCOU, altitudes et GPS.

### Bloc « Avant de commencer »

- Durée : 2 h.
- Prérequis : 9.1 à 9.3.
- À la fin : le journal du Crash Proof complet et comparé aux Notes CP ; puis le défi sur le deuxième log.
- À poster : le journal du défi.

### 1. Le même motif partout

Tous les contrôleurs se lisent de la même façon : target contre actual, overshoot ou undershoot, ratio P/D dans le bon sens, D en dernier. Ce qui change, c'est le nom du message de log et le nom des paramètres, et ArduPilot n'est pas cohérent (D veut dire Desired dans un message et dérivée dans un autre ; T veut dire Target ; V veut dire vitesse en anglais dans PSCN). C'est la raison d'être de la fiche des contrôleurs.

Deux règles avant de commencer :

- **DT constant.** Le time step entre deux itérations (visible dans les messages PID) doit rester stable, 1/400 s. S'il monte, il y a du lag dans le système, et rien de ce qui suit n'est fiable. C'est aussi le paramètre le plus critique à gérer quand on écrit soi-même un contrôleur.
- **Ratio signal sur bruit d'environ 10.** Si l'actual vibre autour de la target avec une amplitude qui dépasse un dixième du signal, il faut filtrer (les passe-bas internes du contrôleur, `FLTT` sur la target, `FLTE` sur l'erreur, `FLTD` sur la dérivée) avant de régler les gains. Sur le Crash Proof, l'accélération verticale vibrait à 20 sur 250 : limite, on note, on n'agit pas encore.

### 2. Les contrôleurs d'angle

- Messages : ATT (DesRoll contre Roll, DesPitch contre Pitch, DesYaw contre Yaw).
- Paramètres : `ATC_ANG_RLL_P`, `ATC_ANG_PIT_P`, `ATC_ANG_YAW_P`. **Il n'y a qu'un P.** Pourquoi : si le contrôleur de rate est bon, quand on demande 0 degré par seconde on l'obtient, donc il n'y a pas d'inertie à freiner au niveau de l'angle ; c'est le rate qui s'occupe de l'inertie. C'est le moment de faire comprendre que « PID » est un nom générique et que beaucoup de contrôleurs de la chaîne n'ont qu'un P.
- Crash Proof : roll 18 demandé, 19,4 obtenu, environ 10 % d'overshoot ; pitch pareil. Hypothèse : réduire P de 10 % sur les deux. Yaw angle : un peu de délai, normal puisque le rate yaw manquait de P ; on ne touche pas.
- Mise à l'échelle dans UAV Log Viewer : zoomer sur une section, ajuster les axes, dézoomer. C'est fastidieux et il faut le dire.

### 3. La chaîne verticale

À lire sur une portion en AltHold.

- Vitesse verticale : CTUN DCRt contre CRt (desired climb rate contre climb rate). Paramètres `PSC_VELZ_*`. Crash Proof : bien fité, pas assez de données pour conclure, on ne touche pas.
- Accélération verticale : PIDA (Tar contre Act). Paramètres `PSC_ACCZ_P`, `PSC_ACCZ_I`, `PSC_ACCZ_D` (D à 0 par défaut). Crash Proof : undershoot, 330 contre 440, environ 20 à 25 % ; hypothèse : `PSC_ACCZ_P` plus 20 %.
- Position verticale : CTUN DAlt contre Alt. Paramètre `PSC_POSZ_P`, un P seul. Crash Proof : un peu d'overshoot ici, d'undershoot là, pas de grandes variations d'altitude dans le vol, donc pas de conclusion. Le vol de tuning suivant doit inclure des montées et descentes franches.
- Les noms changent entre ArduCopter 4.6 et 4.7 ; la fiche donne les deux.

### 4. La chaîne horizontale

À lire en Loiter ou Guided. Messages PSCN et PSCE (nord et est) qui regroupent position (TPN contre PN), vitesse (TVN contre VN) et accélération (TAN contre AN ; la différence entre desired et target est probablement le filtrage, à confirmer). Paramètres `PSC_POSXY_P` (P seul), `PSC_VELXY_P/I/D`, accélération. Six contrôleurs. Les valeurs par défaut sont bonnes ; on les règle quand même « parce que ça fait partie du plaisir ». C'est l'exercice que Colin a laissé à Tom en fin de séance : la formation le laisse aussi à la recrue.

### 5. La marge de contrôle

Avant de monter n'importe quel gain, regarder RCOU (les PWM moteurs, « servo out » inclut les moteurs).

- La plage : de `MOT_SPIN_MIN` (1 050 à 1 080 environ, 8 à 9 %) à 2 000.
- Si un moteur touche le plancher pendant une manœuvre, il ne peut plus donner moins ; s'il touche le plafond, plus. Toucher le plancher se rattrape souvent ; toucher le plafond est grave.
- Des moteurs qui « collent » au plancher ou au plafond pendant un vol autonome veulent dire manque d'autorité ou gains trop agressifs. C'est la limite physique à la montée du ratio P/D et de l'agressivité.
- En Stabilize, le pilote peut faire toucher le plancher lui-même en coupant les gaz : ce n'est pas un problème de contrôle.
- Crash Proof pendant les coups de stick : minimum 1 250, énorme marge, on peut monter les gains.
- Monter `ATC_RAT_YAW_P` monte l'amplitude des écarts entre moteurs en yaw : à chaque hausse, se demander si la marge existe.

### 6. Le journal d'hypothèses et l'ordre des vols

La démarche complète, telle que formulée en fin de séance :

1. **Réglage initial** d'après les fiches techniques (fréquence moteur estimée, filtres larges parce qu'on ne sait rien, gains prudents). Voir la question 3 : est-ce que la formation le couvre ?
2. **Premier vol** avec la routine : hover calme, coups de stick par axe, un peu d'AltHold, un peu de Loiter.
3. **Revue et corrections initiales** : c'est cette formation. On note des hypothèses, pas des certitudes.
4. **3 à 10 vols** à valider et affiner les PID, de bas en haut. Les filtres se revérifient à chaque fois.
5. **Agressivité** : une fois les PID solides, monter les limites (rates max, accélérations max, jerk) en vérifiant que le drone atteint la commande (500 degrés par seconde demandés, 500 obtenus sur le Crash Proof, pas sur EXA) et que les vibrations tiennent.
6. **Feed-forward** vers le troisième vol.
7. **Refaire les filtres** à tout changement mécanique ou de charge utile.

Le journal, tel qu'il existe déjà sur Notion (« Notes CP ») en version brute, à formaliser :

| Vol | Contrôleur | Observation | Hypothèse (paramètre, sens, %) | Appliqué ? | Résultat au vol suivant |
|---|---|---|---|---|---|
| 1 | Rate yaw | Undershoot 121/146, step response plafonne à 0,78 | `ATC_RAT_YAW_P` plus 30 % | oui, en vol | |
| 1 | Angle roll | Overshoot 19,4/18 | `ATC_ANG_RLL_P` moins 10 % | | |
| 1 | Accel Z | Undershoot 330/440 | `PSC_ACCZ_P` plus 20 % | | |
| 1 | Filtres | Sur-filtré, notch à côté | notch 112 Hz, BW 12, 5 dB, 3e harm. ; LPF 400 Hz | oui, avant le vol 2 | |

La page Notion « Analyse de test de vol » a déjà une table par véhicule (date, résumé, anomalies, actions de suivi) : le journal peut vivre là, une ligne par vol, avec le tableau ci-dessus en sous-page. Voir la question 10.

### 7. Lire un vol qui a mal tourné

Ce qui a le plus marqué la séance, et qui manque à toutes les autres formations : les logs disent ce qui s'est vraiment passé, y compris ce que le pilote n'a pas dit ou ne sait pas qu'il a fait.

- **RCIN** : les entrées pilote, canal par canal (il faut connaître le mapping de la manette : RC3 throttle, quel canal arm, etc.). L'épisode AltHold du Crash Proof, reconstruit : le pilote monte au-dessus de 50 % de gaz, le drone reset son altitude, le pilote redescend le stick, le drone continue de monter, le pilote descend à 1 105, le drone monte toujours, oscillation qui s'amplifie, disarm à 6 m, tentative de rearm (mode emergency disarm non activé), impact. Cause : le PID vertical était dix fois trop bas, le drone répondait avec un retard que personne ne peut piloter.
- Ce que ça enseigne : distinguer erreur logicielle et erreur de pilotage, les temps de réaction, et **valider ce que le pilote dit avoir fait** contre ce que le log montre (Colin lui-même n'avait pas mentionné la tentative de rearm).
- **Les sources d'altitude** : estimé EKF, baromètre, GPS, rangefinder, dans des repères différents (sol au décollage, niveau de la mer, distance au sol). Le baro dérive ; le GPS vertical est mauvais (2,5 à 3 m sur un M10) ; le rangefinder ne dérive pas et corrige l'estimé. Sur le Crash Proof, pas de rangefinder actif, donc pas d'estimé fiable. Quand un problème d'altitude arrive, c'est la combinaison des sources qu'il faut comprendre.
- **GPS** : le glitch, c'est une perte momentanée de satellites (15 à 12) avec une hausse de l'imprécision horizontale (1 à 1,3 m à 2,2 m), sur environ 20 secondes. Le GPS croit s'être déplacé. Les paramètres de glitch disent à l'EKF de se fier aux IMU pendant ce temps. Beaucoup de glitchs = interférence, câblage, changer de GPS. Ground speed, nombre de satellites au fil du vol.
- **Les événements** : arm, interlock, yaw reset, hover appris, changements de mode. On superpose toujours l'altitude pour se repérer.
- **Être créatif dans le croisement** : entrée pilote contre sortie moteur contre voltage ; quel capteur était connecté à quel moment lors d'un vol où tout s'est éteint. C'est ce qui permet d'aller plus loin que la formation.

### 8. Défi

Sur le deuxième log (question 6) : remplir la fiche de santé, produire les paramètres de filtre, noter les hypothèses rate, angle, vertical, et reconstruire un événement du vol choisi par Colin (par exemple « pourquoi le drone a dérivé à 3 min 20 »). Livrable : le journal, posté sur Discord. Solution : le journal de Colin pour ce log, dans `solutions/`, publié après la première cohorte.

> Tu as réussi si : ton journal contient une hypothèse par contrôleur, chacune avec un paramètre, un sens et un pourcentage, et la reconstruction de l'événement colle aux entrées RCIN.

### Images à fournir

- ATT DesRoll contre Roll zoomé et mis à l'échelle, idem pitch.
- CTUN DCRt contre CRt en AltHold ; PIDA Tar contre Act avec la zone bruitée ; DAlt contre Alt.
- PSCN position, vitesse, accélération.
- RCOU des quatre moteurs avec MOT_SPIN_MIN annoté, pendant les coups de stick et pendant l'épisode Stabilize où ça touche le plancher.
- RCIN throttle contre altitude sur l'épisode AltHold, avec le canal arm.
- Les quatre sources d'altitude superposées.
- GPS NSats et HAcc sur le glitch.
- La table d'événements autour d'un arm.

---

## 6. Ce que le transcript ne couvre pas et que le plan d'apprentissage annonce

Le bloc B9 du plan dit : « PID, filtres, configurations, failsafes, démarche générale de tuning », plus « analyse post-vol : tlogs et dataflash dans Mission Planner, rosbags côté ROS 2 », plus un lien croisé avec `TerminationSystem` pour les failsafes logiciels. La séance du 11 août couvre PID, filtres, démarche, et la lecture des logs dataflash. Restent :

- **Configurations initiales** avant premier vol (calibrations, `MOT_SPIN_MIN`, `MOT_THST_HOVER`, moniteur batterie, nombre de pôles, notch en mode throttle, gains prudents, limites de rate basses). Question 3.
- **Failsafes** (radio, batterie, GCS, EKF, fence, et le lien avec `TerminationSystem`). Rien dans la séance. Question 3.
- **AutoTune et QuikTune**, la voie officielle d'ArduPilot. Pas un mot dans la séance. Question 7.
- **Rosbags**. Le plan les rattache à B9 ; ils n'ont rien à voir avec le tuning ArduPilot et tout à voir avec la formation 3. Question 11.
- **Les tlogs dans Mission Planner** (rejouer un vol, relire les messages) : une section courte dans 9.1 suffit, mais il faut le tlog du 11 août pour l'illustrer, et l'avertissement jaune reçu ce jour-là n'a jamais été relu.

---

## 7. Les annexes et le matériel

- **La fiche des contrôleurs** (`controleurs-arducopter-4.6-4.7.html` sur la page Notion « Tuning guide ») : modes de vol et contrôleurs actifs, et pour chaque contrôleur le message de log, les champs target et actual, les paramètres 4.6 et 4.7. C'est l'annexe centrale de 9.4 et il faudra la convertir en markdown dans le dépôt. Elle a été générée avec Claude et n'est « pas complètement révisée » : à relire avant publication. Je n'y ai pas accès par l'API Notion ; il faut le fichier.
- **Le schéma de la chaîne de contrôleurs**, même origine, même remarque.
- **Le log de la séance**, retrouvé et vérifié le 15 septembre : c'est le vol du **8 août 2026, 16 h 17** (140 Mo, 24,5 min, ArduCopter 4.6.3 sur MatekH743, modes Stabilize, AltHold, Loiter). Ses paramètres sont ceux vus à l'écran : notch à 102 Hz en mode throttle, bandwidth 25, atténuation 15, passe-bas gyro 42 Hz, hover appris 0,125, yaw rate P 0,18, angle P 4,5, PSC_ACCZ_P 0,15. Copié dans `9-tuning/logs/crash-proof-vol1-2026-08-08.bin` (original : `Desktop\Aerialix\_tri\2026-08\2026-08-08 16-17-28.bin`). Trop gros pour GitHub : le dossier `logs/` est ignoré par git, il faudra un lien (question 6). Aucun `.tlog` de ce vol n'a été retrouvé dans les logs de Mission Planner.
- **Le vol suivant**, le 11 août à 16 h 58 (135 Mo, 19 min), reçu par WeTransfer et copié dans `9-tuning/logs/crash-proof-vol2-2026-08-11.bin`, plus un vol court de 2,4 min à 16 h 55 (`crash-proof-vol2a-2026-08-11-court.bin`). Ses paramètres montrent ce qui a réellement été appliqué après la séance : yaw rate P 0,24 (plus 33 %), angle roll et pitch P 4,05 (moins 10 %), PSC_ACCZ_P 0,18 (plus 20 %), notch 111 Hz en mode télémétrie ESC, options 14 (multisource, loop rate, toutes les IMU), bandwidth 12, atténuation 6. **Le passe-bas gyro est resté à 42 Hz** : le passage à 400 Hz décidé en séance n'a pas été appliqué. C'est un excellent cas pour la formation (vérifier ce qui a vraiment été chargé, la règle « comparer deux fois ») et une question pour toi : oubli, ou choix après coup ?
- **Un deuxième log pour le défi** : le vol 2 du Crash Proof est un candidat naturel (même drone, la recrue vérifie si les hypothèses du vol 1 se sont confirmées), mais un vol d'EXA donnerait le contraste sur le yaw.
- **Un glossaire** : target, actual, step response, overshoot, undershoot, amortissement critique, dB, notch, passe-bas, harmonique, phase, hover, sag, clipping, loop rate, DT, autorité, marge de contrôle.
- **Une table « quand ça casse »** propre au tuning : le log ne charge pas (taille), Filter Review n'affiche pas le post-filtre (option batch), le RPM est un multiple de l'attendu (pôles), PID Review n'a pas de courbes pour un contrôleur (pas logué par défaut), les courbes UAV Log Viewer ne sont pas à l'échelle, le notch affiché n'est pas à la fréquence du paramètre.

---

## 8. Questions à trancher avant la rédaction

Je les pose dans l'ordre où elles bloquent.

1. **Le numéro.** Le plan d'apprentissage dit B9, parallèle à partir de B3, rattaché à l'objectif 6 (24 octobre). Tu parlais de B5 ou B6. Dans le dépôt, il n'y a que 0 à 4. Trois options : `9-tuning` tel que le plan (cohérent avec la carte Notion à publier le 18 septembre), `5-tuning` en renumérotant le plan (B5 architecture de mission devient B6, etc.), ou un numéro hors séquence parce que c'est une branche parallèle. Je recommande de suivre le plan : 9. Et le prérequis réel n'est pas B3 mais B1 seulement (Mission Planner et paramètres) ; le plan dit « objectifs 2 à 4 », ce qui exclurait les recrues qui ne font pas ROS mais veulent faire du tuning. À confirmer.

2. **Un ou quatre documents, et le budget.** Quatre documents font environ 6 h 30 pour la recrue et bien plus que 8 h de rédaction pour toi. L'audit a montré que B3 a triplé par rapport au plan. Alternative : deux documents (9.1 lire et vérifier ; 9.2 régler et itérer), plus courts, en reportant la chaîne horizontale et la lecture d'un vol raté dans une « suite » non planifiée. Je recommande quatre documents mais avec 9.4 marqué comme optionnel pour la première cohorte.

3. **Où commence la formation ?** Au moment où le log existe (ce que couvre la séance), ou avant, à la préparation du premier vol (configuration initiale, options de log à activer, routine de vol à briefer au pilote, failsafes) ? Le plan annonce « configurations » et « failsafes ». Sans ça, la recrue ne saura pas produire un log utilisable. Je recommande une section « préparer un vol de tuning » en tête de 9.1 (une page : quoi activer, quoi dire au pilote) et une note honnête que les failsafes sont hors périmètre de cette version, à moins que tu aies du contenu.

4. **L'ordre.** En séance : PID Review d'abord (« c'est lui qui donne la meilleure intuition »), puis Filter Review, puis UAV Log Viewer. La page Notion dit : filtres, rates, angle et autres, vérifications. Je propose pour la formation : santé du système, filtres, rates, autres, parce qu'on ne peut pas juger un rate avec un filtre en retard, ni un filtre avec un RPM faux. Mais l'argument de l'intuition est réel : la step response parle tout de suite, le spectre en dB non. Tu tranches.

5. **La profondeur théorique.** Tom n'avait pas fait asservissement et ça a marché. Faut-il un primer P, I, D, échelon, dB, phase (20 minutes, sans équations) dans 9.1, ou un renvoi vers une ressource externe dans la formation 0 ? Je recommande le primer maison, court, avec les images du log plutôt que des courbes théoriques.

6. **Les logs.** Le log du 11 août fait quelle taille ? S'il dépasse ce que GitHub accepte (100 Mo par fichier), il faut un lien (Drive, Notion) et la formation devient dépendante d'un lien. Et quel deuxième log pour le défi : un autre vol du Crash Proof, un vol d'EXA (gros drone, yaw qui ne converge pas, cas d'école), ou le vol où « tout s'est éteint » ? Je recommande EXA pour le contraste.

7. **AutoTune.** C'est la méthode officielle et la première chose qu'une recrue trouvera sur le forum. La séance ne le mentionne pas. Il faut au minimum une section « pourquoi on tune à la main chez Zenith » (gros drones, risques, contrôle de ce qui change, apprentissage) et dire si AutoTune est proscrit, toléré comme point de départ, ou utilisé sur les petits drones. Sinon la recrue conclura que tu ne le connais pas.

8. **La fiche des contrôleurs.** Elle vit sur Notion en HTML. La formation ne peut pas dépendre d'un embed Notion. Je propose de la convertir en `9-tuning/fiche-controleurs.md` dans le dépôt. Il me faut le fichier, et tu dois le relire (il n'est « pas complètement révisé »).

9. **Trois trous factuels de la séance** à combler ou à assumer : l'outil pour découper un log trop gros ; pourquoi Filter Review montrait le notch à 106 Hz pour un paramètre à 102 ; comment on change les gains en vol en pratique (Extended Tuning, canal de tuning radio, GCS). À toi de me dire, sinon j'irai vérifier dans la doc et je marquerai « à confirmer ».

10. **Où vit le journal de tuning.** Notes CP est une page brute. La page « Analyse de test de vol » a une table par véhicule. Je recommande que la formation impose le tableau de la section 5.6 comme format, et que la table Notion par véhicule soit l'index. Ça rend le journal de la recrue comparable à celui des directeurs.

11. **Rosbags.** Le plan les met dans B9 pour l'analyse post-vol. Ils appartiennent à la formation 3 (ROS 2) ; les mélanger au tuning ArduPilot brouille la formation. Je recommande de les sortir de B9 et de les mettre en 3.5 ou en annexe de la formation 3, et de corriger le plan.

12. **Le ton.** La séance est riche parce qu'elle est honnête : « j'ai de la misère à justifier 30 plutôt que 20 », « moi-même j'ai de la difficulté avec la phase », « c'est du gossage ». Je propose de garder cette honnêteté dans le texte (encadrés « ce qu'on ne sait pas bien ») plutôt que de lisser en règles fermes. Ça change la façon d'écrire ; dis-moi si tu es d'accord.

13. **Les images.** Les listes par document ci-dessus font une quarantaine de captures. Toutes viennent du même log, donc reproductibles. Veux-tu que la rédaction se fasse avec des marqueurs d'image nommés (`![...](9.2-05-notch-config.png)`) que tu remplis ensuite, pour que le texte puisse être écrit sans attendre ?

---

## 9. Ce qui a été fait, ce qui reste

Fait : lecture complète du transcript du 11 août, des pages Notion Tuning guide (Tuning 1er → 2 vol, Rate tuning, Filter tuning, ANG + autres, Vérifications, Notes CP), du plan d'apprentissage, des formations 0 à 3 pour les conventions (blocs « avant de commencer », « tu as réussi si », défis, « quand ça casse », solutions).

Reste, dans l'ordre : tes réponses aux questions 1 à 13 ; la fiche des contrôleurs et les deux logs ; puis la rédaction de 9.1 à 9.4 avec marqueurs d'images ; puis ton passage d'images ; puis le test sur une recrue qui n'a jamais fait de tuning, chronométré.
