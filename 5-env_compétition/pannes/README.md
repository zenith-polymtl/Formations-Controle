# pannes/ : trois pannes préfabriquées pour l'exercice du document 5.2

Trois patchs, trois pannes, une par étage. Chacune casse la démo `demo_ws` d'une seule ligne.
La recrue ne lit pas le patch : elle lance la démo, observe, et cherche.

## Avant de commencer

La démo doit tourner. Depuis la racine du clone du dépôt de mission :

```bash
cp -r <dossier de la formation>/5-env_compétition/demo_ws workspaces/
cp workspaces/demo_ws/src/demo_bringup/config/demo.yaml config/
make link C=demo PKG=tools && make link C=demo PKG=custom_interfaces && make link C=demo PKG=sim_mocks
make build C=demo
make sim C=demo
```

Le SITL tourne dans Mission Planner. Dans un second terminal, `make shell C=demo IMG=sim` puis
`ros2 run sim_mocks rc_simulator` : la touche `w` envoie le GO. La démo marche quand
`ros2 topic echo /aeac/external/demo/state` passe de `IDLE` (0) à `GOTO` (1) après le GO.

## Appliquer une panne sans la lire

Depuis la racine du clone. Ne cherchez pas un `git status` vide : vous avez copié `demo_ws` et `demo.yaml`. Ce qu'on demande est qu'il n'y ait pas d'autre modification que celles du patch une fois la panne posée, pour ne pas chercher une panne que vous auriez écrite vous-même.

```bash
git apply pannes/panne-1.patch     # ne pas ouvrir le fichier, c'est tout l'exercice
make sim C=demo
```

## Retirer la panne

```bash
git apply -R pannes/panne-1.patch
find workspaces -maxdepth 1 -type d -empty -exec rmdir {} + 2>/dev/null || sudo find workspaces -maxdepth 1 -type d -empty -exec rmdir {} +
```

La seconde ligne est du ménage : une panne peut laisser un dossier vide dans `workspaces/`,
que `git apply -R` ne retire pas parce que git ne suit pas les dossiers. La commande ne
supprime que des dossiers vides, donc elle est sans danger ; la seconde forme sert quand le
dossier n'appartient pas à l'utilisateur. S'il n'y a rien à retirer, elle ne fait rien.

`git apply -R --check pannes/panne-1.patch` répond sans rien changer si la panne est bien
en place ; `git apply --check` répond sans rien changer si elle peut être appliquée. En cas
de doute, `git status` puis `git checkout -- compose/sim.yml config/demo.yaml` remettent
d'aplomb les deux seuls fichiers que les patchs touchent.

Une panne à la fois : les trois patchs touchent des fichiers différents, mais les appliquer
ensemble apprend à chercher trois choses en même temps, ce qui n'apprend rien.

## L'ordre de recherche : trois étages, toujours dans cet ordre

1. **Conteneur** : est-ce que le conteneur tourne ? `docker ps`, puis `make logs IMG=sim`.
2. **Nœud** : est-ce que le nœud tourne et parle ? `ros2 node list`, `ros2 topic list`, `ros2 topic hz`.
3. **Donnée** : est-ce que les valeurs sont les bonnes ? `ros2 topic echo`, `ros2 param get`.

On ne descend d'un étage qu'une fois l'étage au-dessus vérifié. Une panne de l'étage 1 ressemble
de loin à une panne de l'étage 3, et c'est en sautant des étages qu'on y perd une soirée.

Les numéros des patchs ne suivent pas l'ordre des étages : c'est voulu, la panne ne s'annonce
jamais. Les leads ont la correspondance dans `SOLUTIONS.md`.
