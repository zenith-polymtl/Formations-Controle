# Journal de tuning : Crash Proof, vol du 27 octobre 2026

*Solution de la formation 9. À ouvrir après avoir écrit le vôtre.*

## 1 - Fiche de santé

Loop rate 400 Hz, CPU 29 %, voltage du contrôleur 3,3 V, 0 message perdu, vibrations 1 à 1,5 m/s² (14 au plus), 0 clipping, moteurs à environ 106 Hz en hover, premier vol à 49,3 V. **Sain, données fiables.**

## 2 - Filtres (hover, 350 à 395 s)

- Pics : 105 Hz et 310 Hz, au-dessus de moins 50 dB.
- Filtres du vol : passe-bas à 42 Hz, tout est écrasé (sur-filtré) ; notch bloqué à son plancher de 111 Hz, au-dessus des moteurs.
- Hypothèse : passe-bas 400 Hz ; plancher du notch sous le hover (100 Hz) ; largeur 12, profondeur 6, fondamentale et troisième harmonique.

## 3 - Rates (PID Review)

| Axe | Step response | Hypothèse |
|---|---|---|
| Roll | 0,88 ; essais en vol : 0,07 plafonne, 0,098 juste, 0,13 oscille | rester entre 0,07 et 0,098 |
| Pitch | 0,85 | comme le roll |
| Yaw | 0,77 | P plus 30 à 50 %, en surveillant la marge moteur |

## 4 - Le reste de la chaîne

| Étage | Observation | Hypothèse |
|---|---|---|
| Angle | overshoot d'environ 10 % | P moins 10 % |
| Vertical | pas de montée franche | rien ; montées franches au prochain vol |
| Horizontal | pas de déplacement franc | rien |
| Marge moteur | en yaw, un moteur à 1 136 pour un plancher de 1 090 | peu de marge en bas : monter le P yaw par étapes |

## 5 - Résultats au vol du 28 octobre

| Contrôleur | Appliqué | Résultat |
|---|---|---|
| Filtres | passe-bas 400 Hz, plancher 107 Hz | chaque pic juste sous moins 50 dB |
| Rate roll, pitch | 0,068 | inchangé (0,90 et 0,84) |
| Rate yaw | P 0,24 → 0,35 | plafonne à 0,75 ; un moteur touche le plancher : limite d'autorité |
| Angle | P 4,05 → 3,7 | overshoot 5 à 7 % |
| Vertical | `PSC_ACCZ_P` 0,18 → 0,25 | montées franches bien suivies |

## 6 - Prochain vol

Paramètres chargés et comparés deux fois ; hover calme de 30 s à 5 m ou plus ; coups de stick par axe en AltHold, batteries pleines ; déplacements francs en Loiter.
