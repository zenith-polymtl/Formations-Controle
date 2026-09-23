# Tâche 6 : rédiger le document 5.3, l'annexe des leads, la page « pour plus tard », et raccorder la formation au parcours

Fichiers à créer dans `C:\Users\colin\Zenith\Control-Formations\5-env_compétition\` :
- `5.3-projet-ajouter-un-noeud.md`
- `5.4-annexe-leads-creer-un-environnement.md`
- `5.5-pour-plus-tard.md` (une page)

Fichiers à modifier :
- `C:\Users\colin\Zenith\Control-Formations\README.md` : ajouter les lignes de la formation 5 dans le tableau des modules (5.1, 5.2, 5.3 avec sujets et durées 1 h 45, 2 h 30, 2 h ; une ligne pour l'annexe 5.4 marquée « leads, 20 min »), entre la formation 3.4 et la formation 9.1, dans le même format que les lignes existantes.
- `C:\Users\colin\Zenith\Control-Formations\0-prerequis\0-prerequis-et-poste-de-travail.md` : le tableau du parcours (vers la ligne 11) reçoit une ligne « Formation 5 | L'environnement de compétition : le dépôt de mission, une mission en simulation, un nœud de plus | 6 h 15 ». Ne change rien d'autre à ce fichier.
- `5-env_compétition\objectifs.md` : garder le contenu, ajouter en tête, après le titre, une ligne « Documents : 5.1, 5.2, 5.3, annexe 5.4 (leads), 5.5 » avec les liens.

Lis dans l'ordre :
1. `style-docs.md` (même dossier que ce brief).
2. Le plan, sections 4, 5 et 6 (lignes 216 à 291) de `C:\Users\colin\Zenith\Control-Formations\5-env_compétition\revue et architecture\PLAN-FORMATION-5.md` : spécification des trois fichiers.
3. Les documents 5.1 et 5.2 déjà écrits dans `5-env_compétition\` (continuité, ne pas répéter).
4. Le matériel : `5-env_compétition\5.3-projet\` en entier (README, squelette, solution, CHECKLIST) et `demo_ws\`.
5. Dans `C:\Users\colin\Zenith\aeac-2027` : `ARCHITECTURE.md` (règles de code, section « Pour les leads »), `README.md` (section « Créer un dépôt de mission à partir de ce template »), `Makefile` (`check`, `link`, `bump`, `deploy`), `scripts/check.py`, `packages/README.md`, `systemd/install.md`, `compose/` et `docker/` (les en-têtes), `packages/tools/tools/topics.py`.
6. `C:\Users\colin\Zenith\Control-Formations\0-prerequis\0-prerequis-et-poste-de-travail.md`, la section sur Git (cherche « git ») pour savoir ce que la recrue a vu en B0 et ne pas le réenseigner.

## 5.3 : projet, ajouter un nœud à la démo

Structure du plan, section 4 : objectifs, bloc « avant de commencer » (2 h ; prérequis 5.2 ; à la fin une PR ouverte sur le dépôt de cohorte et `make check` vert ; à poster : le lien de la PR et une capture du nouveau topic vu depuis un second terminal), puis :
1. Le cahier des charges (texte du plan, repris du README de `5.3-projet`).
2. Le squelette et les règles : où copier le squelette (`workspaces/demo_ws/src/demo_monitor/`), la liste des six règles chacune avec la ligne du squelette ou de la solution qui la respecte (cite les lignes réelles), la constante à ajouter dans `packages/tools/tools/topics.py` avec l'explication : c'est un sous-module, donc dans la vraie vie c'est une PR dans `tools` faite avec un lead ; ici on modifie la copie locale et `make status` dira « modifié localement », c'est attendu et c'est la seule fois où on l'accepte.
3. Brancher et vérifier : ajouter le nœud au launch (montre le bloc à ajouter, cohérent avec `solution/mission.launch.py.diff`), lire `battery_warn_v` dans `demo.yaml` (déjà présent), `make build C=demo`, `make sim C=demo`, le topic dans un second terminal (`ros2 topic echo` du résumé), puis `make check` : montrer sa sortie attendue avec les trois lignes sur le `package.xml` du squelette (reconstruis-la d'après `check.py` : format `chemin: message`), et dire que c'est l'exercice.
4. Rappel git puis branche et PR : quinze minutes, les commandes dans l'ordre exact du plan (`git status`, `git switch -c prenom/monitor`, `git add -p`, `git commit`, `git push -u origin prenom/monitor`, la PR dans le navigateur sur le dépôt de cohorte), une phrase par commande sur ce qu'elle fait ; les trois règles et rien d'autre ; `make check` avant la PR ; le lead relit avec la CHECKLIST. Précise que le sous-module modifié (`packages/tools`) n'entre pas dans le commit du dépôt de cohorte tel quel : `git add -p` ne doit pas stager le pointeur `packages/tools` ; la ligne de `topics.py` est décrite dans la PR pour que le lead la porte dans `tools`. Si `git status` montre `packages/tools (modified content)`, c'est normal.
Table « Quand ça casse » : les quatre lignes du plan.
Termine par « Suite : [Formation 5.5, pour plus tard](5.5-pour-plus-tard.md). Les leads lisent aussi [l'annexe 5.4](5.4-annexe-leads-creer-un-environnement.md). »

## 5.4 : annexe pour les leads

Plan, section 5. Un document court (vingt minutes de lecture), titre qui dit « leads », préambule de trois phrases : la recrue sait que ça existe et ne le fait pas ; écrit pour qu'un lead de 2028 s'en serve sans nous. Six recettes en gestes, chacune avec ses commandes exactes tirées du dépôt :
1. Créer un dépôt de mission (ou de cohorte) à partir de `mission-template` : la recette du README d'aeac-2027, complétée par ce qui y manque (création du dépôt GitHub, droits de l'équipe, première branche protégée `main`, `git push`). Ajoute une variante « dépôt de cohorte pour la formation 5 » : copier aeac-2027 plutôt que le template, retirer ce qui ne sert pas, nommer `formation-5-<cohorte>`.
2. Ajouter une mission : `workspaces/<nom>_ws/src/<nom>_bringup` (launch, `config/<nom>.yaml`), `make link` des partagés, `gcs_ws/src/gcs_bringup/launch/<nom>.launch.py`, `make check`.
3. Ajouter un paquet partagé : la règle local / partagé de `packages/README.md`, puis le geste : dépôt GitHub avec `package.xml` à la racine, `git submodule add`, ligne dans `packages/README.md`, `make bump` dans les autres dépôts qui le suivent.
4. Ajouter un conteneur : un Dockerfile dans `docker/`, un compose dans `compose/`, l'en-tête « ce qui diffère », une cible dans le Makefile, la liste `SERVICES` si c'est un service.
5. Ajouter un service au boot : le fichier dans `systemd/`, `install.md`, l'ordre de dépendance (`After=`), en renvoyant à la formation 6 pour le détail.
6. Faire évoluer : `make bump PKG=`, `make deploy C=`, la section « Pour les leads » d'`ARCHITECTURE.md`, le tag de fin de compétition.
Une phrase de fin : la relecture d'une PR de recrue avec la CHECKLIST de `5.3-projet/solution/`.

## 5.5 : pour plus tard

Plan, section 6. Une page : l'annexe des leads (à parcourir une fois), `procédure.md` (à lire une fois), la formation 6 (réseau, Zenoh, services, capteurs : ce que la 5 a nommé en une phrase et que la 6 ouvre), la formation vision à venir (`vision_ws`, les modèles, la ZED). Une ou deux phrases par item, un lien quand le fichier existe.

Rapport : écarts plan / dépôt tranchés, `wc -w` des trois documents, le diff des trois fichiers modifiés (README, 0-prerequis, objectifs).

Contraintes : aucun tiret cadratin ; aucun commit ; ne modifie aucun autre fichier que ceux listés.
