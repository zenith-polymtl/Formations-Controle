# Exploration : la mission en simulation et la mission démo

> **Décision (Colin, 21 septembre 2026)** : `make sim` utile mais minimal : `sim:=true` ne fait que passer un paramètre aux nœuds, comme en 2026 ; les mocks se lancent à la main, en avant-plan. SITL externe (Mission Planner) reste la référence. Nœuds de test qui arment autorisés sous le paramètre `sim`. Démo dans la formation 5 (M2). Intégré dans `PLAN-ARCHITECTURE-aeac-2027-v3.md`, P21, P25, P26.

*21 septembre 2026. Répond aux réserves de Colin sur P25 (« je ne suis pas sûr de comprendre ») et P26 (« mission démo, pas complètement sûr ; potentiellement dans la formation plutôt que dans aeac-2027 ») de la V1 du plan. Ce document dit concrètement ce que `make sim` lance, ce qu'un nœud fait en mode `sim`, et où la mission démo devrait vivre.*

---

## 1. Ce que « la mission en simulation » veut dire, concrètement

Le point de départ est ce que les formations 1 à 3 font déjà : SITL ArduPilot lancé depuis Mission Planner sous Windows, mavros dans un conteneur qui s'y connecte en TCP sur le port 5762 (`make mavros-sim`, déjà dans aeac-2026 et dans la formation 3), et une node maison qui pilote via mavros. La mission en simulation, c'est la même chose avec le code de mission complet à la place de la node de la formation 3.4, et des mocks pour ce que SITL ne simule pas.

| Élément | En vol | En simulation (`make sim C=<mission>`) | Qui le fournit |
|---|---|---|---|
| Autopilote | Pixhawk, mavros en serial sur la Jetson | SITL dans Mission Planner (ou Gazebo, formation 4), mavros en TCP 5762 | Formations 1 et 3, déjà en place |
| Conteneur de mission | Image `drone` sur la Jetson, lancé par systemd | Image `gcs` sur le poste WSL, lancé par `make sim` en avant-plan | `compose/sim.yml` |
| Manette (interrupteurs RC) | Récepteur ELRS, topic `/mavros/rc/in` | `rc_simulator` : touches clavier vers `/mavros/rc/in` (existe en 2026) | `sim_mocks` |
| Caméra ZED et détections | Conteneur vision, YOLO, topic de détections | `target_mock` : publie une détection fixe ou mobile sur le même topic (existe en 2026 sous le nom `target_detection_mock`) | `sim_mocks` |
| Cible physique (feu, zone) | Le terrain | Une coordonnée dans `config/sites/sim.yaml` | Config |
| Actionneur (servo, valve, pompe) | PWM via mavros | Le même nœud, en mode `sim` : il loggue « aurait tiré » au lieu d'envoyer le PWM | Paramètre `sim:=true` du nœud |
| Zenoh, GCS distante | Deux machines, pont Zenoh | Tout sur une machine, domaine 3, pas de Zenoh | `sim.yml` |

Le résultat attendu : `make sim C=water` sur un poste WSL, et dans Mission Planner on voit le drone simulé faire la mission 2 du début à la fin, pendant que `ros2 topic echo` montre la machine à états changer d'état. Sans Jetson, sans ZED, sans manette.

## 2. Ce que `sim:=true` fait dans un nœud

Un seul paramètre, déclaré par les nœuds qui parlent au matériel, et propagé par le launch de la mission. Trois comportements possibles, à choisir par nœud :

1. **Rien à faire** : le nœud ne parle qu'à mavros et à d'autres nœuds ; SITL suffit. C'est le cas de `nav_stack`, des machines à états, des heartbeats. La majorité.
2. **Remplacer une entrée** : le nœud lit un topic matériel (`/mavros/rc/in`, détections) ; en sim, un mock publie sur le même topic, le nœud ne change pas. C'est le rôle de `sim_mocks`.
3. **Neutraliser une sortie** : le nœud commande un actionneur ; en sim, il loggue l'action au lieu de l'envoyer. Le paramètre `sim` est lu une fois au démarrage, et la branche `if self.sim:` entoure le seul appel matériel.

`auto_approach.py` de 2026 a déjà un mode `sim` de ce genre (revue 2). La règle du template : un nœud qui touche au matériel expose `sim`, les autres non.

## 3. Ce que `make sim` lance, ligne par ligne

```
make sim C=water
  → docker compose -f compose/sim.yml up            image gcs, dépôt monté, domaine 3
      service mavros-sim : mavros vers tcp://<IP Windows>:5762   (formation 3)
      service mission    : ros2 launch water_bringup mission.launch.py sim:=true site:=sim
  → le launch de mission, avec sim:=true, inclut sim_mocks/launch/mocks.launch.py
      rc_simulator, target_mock, avec les topics de topics.py
```

Le launch de la mission est le même qu'en vol. `sim:=true` ne fait que deux choses : passer le paramètre aux nœuds, et inclure les mocks. Il n'y a pas de « launch sim » séparé à maintenir, donc il ne peut pas diverger du launch réel.

## 4. Où vit la mission démo

Le problème : avec « squelette + générique seulement », le template ne contient aucune mission, donc `make sim` n'a rien à lancer et la formation 5 n'a rien à faire tourner. Il faut une mission quelque part. Trois emplacements possibles.

### M1 : dans le template, donc dans aeac-2027 (V1 du plan)

`packages/demo_bringup` livré avec le template et copié dans aeac-2027.
- La recrue clone aeac-2027 et lance `make sim C=demo` : premier contact réel avec le vrai dépôt.
- Mais aeac-2027 traîne une mission fictive à côté des vraies. Elle sera périmée dès que `tools` évolue, et quelqu'un finira par la supprimer ou par la laisser casser. C'est la réserve de Colin, et elle est juste.

### M2 : dans la formation 5, comme exercice guidé

Le dossier `5-env_compétition/` contient `demo_ws/` avec la mission démo, sur le modèle de `b3_tools_ws` de la formation 3. La formation guide la recrue : copier `mission-template/`, y déposer `demo_ws` comme `workspaces/demo_ws`, lier les paquets partagés, lancer `make sim C=demo`. Puis les exercices modifient la démo (ajouter un état, changer le YAML, retrouver un câblage mort).
- aeac-2027 ne contient jamais la démo. Le template non plus : il est purement infra et paquets génériques.
- La démo vit avec la formation, qui est l'endroit où on la maintient et où on la lit.
- La recrue fait le geste « ajouter une mission au template » elle-même, ce qui est exactement ce qu'elle fera en 2027.
- Coût : `demo_ws` dépend de `tools` et `custom_interfaces` (par symlinks vers `mission-template/packages/`, qui les contient en sous-modules). Quand ces paquets évoluent, la formation doit suivre, comme toutes les formations.

### M3 : dans le template, retirée à la création d'aeac-2027

Compromis : le template contient `demo`, et la procédure « créer un dépôt de mission » dit de la supprimer.
- Une étape de plus, oubliée une fois sur deux ; et la démo n'est de toute façon lue qu'en formation.

## 5. Comparaison

| Critère | M1 template | M2 formation | M3 template puis retrait |
|---|---|---|---|
| aeac-2027 propre | Non | Oui | Si on pense à la retirer |
| La formation a quelque chose à lancer | Oui | Oui | Oui |
| Qui maintient la démo | Le dépôt de mission (personne) | La formation (Colin, puis le prochain responsable formations) | Le template |
| La recrue apprend à ajouter une mission | Non, elle est déjà là | Oui, c'est l'exercice | Non |
| Dépendance formation → template | Faible | Forte (la démo compile contre les paquets du template) | Faible |

## 6. Recommandation

**M2.** La démo est un contenu de formation, pas un contenu de mission. Le template ne contient que ce qui survit d'une année à l'autre : infra, `sim_mocks`, `compose/sim.yml`, et les paquets partagés. `make sim C=<mission>` existe dans le template et sert à toute vraie mission 2027 ; la formation 5 lui donne sa première mission.

Contenu de la démo, inchangé par rapport à la V1 : une machine à états de quatre états (`IDLE`, `GOTO`, `ACT`, `RETURN`), un « GO » externe, un waypoint du YAML, un service d'action factice, retour. États en constantes de `custom_interfaces`, `_transition()` unique et loggé, mode `sim`, topics de `topics.py`. Une centaine de lignes, et le modèle de toute mission 2027.

Conséquence pour le plan V2 : P25 est reformulé avec la table de la section 1 ; P26 devient « la mission démo vit dans la formation 5 », effort inchangé mais imputé à la formation, pas au template.

## 7. Questions pour la discussion

- SITL depuis Mission Planner (Windows) reste la référence, comme dans les formations 1 à 3 ? Gazebo (formation 4) serait une option de `make sim`, pas la voie par défaut.
- Les nœuds de test qui arment ou changent de mode en simulation (autorisés par Colin sur P21) : dans `sim_mocks` avec un suffixe `_test`, et jamais inclus par un launch de mission ?
- `rc_simulator` lit le clavier du terminal : en avant-plan dans `make sim`, ça fonctionne ; dans un conteneur détaché, non. `make sim` reste en avant-plan, comme `make mavros-sim` en formation 3 ?
