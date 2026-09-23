#!/usr/bin/env python3
"""`make check` : vérifie le dépôt avant une PR. Une ligne par problème, code de retour 1 s'il y en a.

Vérifie : les package.xml (mainteneur, licence, description), les dossiers test/ générés par
ros2 pkg create, les symlinks cassés dans les workspaces, les sous-modules non initialisés,
les cibles make citées dans README.md et ARCHITECTURE.md qui n'existent pas, et les fichiers
de docker/ que personne ne lit.
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
problems = []


def problem(path, message):
    problems.append(f'{path.relative_to(ROOT) if isinstance(path, Path) else path}: {message}')


# 1. package.xml : mainteneur, licence, description
for pkg in ROOT.glob('**/package.xml'):
    if any(part in ('build', 'install', 'log') for part in pkg.parts):
        continue
    text = pkg.read_text(encoding='utf-8', errors='replace')
    if re.search(r'<maintainer[^>]*>[^<]*todo', text, re.I) or 'todo.todo' in text:
        problem(pkg, 'mainteneur à remplir')
    if re.search(r'<license>\s*(TODO.*|)\s*</license>', text, re.I):
        problem(pkg, 'licence à remplir (Apache-2.0)')
    if re.search(r'<description>\s*(TODO.*|)\s*</description>', text, re.I):
        problem(pkg, 'description à remplir')
    # 2. dossier test/ template (les trois fichiers identiques de ros2 pkg create)
    test_dir = pkg.parent / 'test'
    if test_dir.is_dir():
        names = {p.name for p in test_dir.iterdir()}
        if names >= {'test_copyright.py', 'test_flake8.py', 'test_pep257.py'}:
            problem(test_dir, 'dossier test/ généré par ros2 pkg create : à supprimer (pas de tests dans ce dépôt)')

# 3. symlinks cassés dans les workspaces
for src in ROOT.glob('workspaces/*/src'):
    for entry in src.iterdir():
        if entry.is_symlink() and not entry.exists():
            problem(entry, f'symlink cassé vers {entry.readlink()}')

# 4. sous-modules non initialisés
gitmodules = ROOT / '.gitmodules'
if gitmodules.exists():
    for m in re.finditer(r'path\s*=\s*(\S+)', gitmodules.read_text()):
        path = ROOT / m.group(1)
        if not path.is_dir() or not any(path.iterdir()):
            problem(path, 'sous-module vide : lance make init')

# 5. cibles make citées dans la doc
makefile = (ROOT / 'Makefile').read_text(encoding='utf-8')
targets = set(re.findall(r'^([a-zA-Z0-9_%-]+):', makefile, re.M))
pattern_targets = [t for t in targets if '%' in t]
for doc in ('README.md', 'ARCHITECTURE.md', 'procédure.md'):
    doc_path = ROOT / doc
    if not doc_path.exists():
        continue
    for cited in set(re.findall(r'\bmake\s+([a-zA-Z0-9_-]+)', doc_path.read_text(encoding='utf-8'))):
        ok = cited in targets or any(re.fullmatch(t.replace('%', '.+'), cited) for t in pattern_targets)
        if not ok:
            problem(doc_path, f'cite `make {cited}` qui n\'existe pas dans le Makefile')

# 6. fichiers de docker/ que personne ne lit
docker_dir = ROOT / 'docker'
if docker_dir.is_dir():
    dockerfiles = list(docker_dir.glob('dockerfile.*'))
    compose_text = ''.join(p.read_text(encoding='utf-8') for p in (ROOT / 'compose').glob('*.yml'))
    dockerfile_text = ''.join(p.read_text(encoding='utf-8') for p in dockerfiles)
    for f in docker_dir.iterdir():
        if f in dockerfiles:
            if f.name not in compose_text:
                problem(f, 'aucun compose ne construit cette image')
        elif f.name not in dockerfile_text:
            problem(f, 'aucun Dockerfile ne lit ce fichier : le supprimer ou le lire')

if problems:
    print('\n'.join(problems))
    sys.exit(1)
print('check : rien à signaler')
