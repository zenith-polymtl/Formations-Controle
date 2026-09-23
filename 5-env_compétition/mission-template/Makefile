# Makefile du dépôt de mission. Trois sections :
#   1. Développement et simulation  (poste WSL)
#   2. Test sur véhicule            (Jetson ou portable, à la main, en avant-plan)
#   3. Déploiement                  (Jetson, systemd ; leads)
# `make help` liste les cibles par section. Lire ARCHITECTURE.md avant tout.

# ----- Variables (surchargeables : make build C=water IMG=drone) -----
# C     : la mission, donc le workspace workspaces/$(C)_ws
# IMG   : le conteneur dans lequel on travaille : dev | drone | gcs | vision | sim
# DRONE : la config Zenoh sol, config/drones/$(DRONE).json5
C      ?= gcs
IMG    ?= dev
DRONE  ?= hexa
WS     := workspaces/$(C)_ws
COMPOSE := compose/$(IMG).yml
# IP de Windows vue depuis WSL, pour joindre le SITL de Mission Planner (tcp 5762)
SITL_HOST ?= $(shell ip route 2>/dev/null | awk '/default/ {print $$3; exit}')
MODELS_URL ?=
export C IMG DRONE SITL_HOST

SERVICES := lo-multicast mavros zed zenoh-air vision mission

.DEFAULT_GOAL := help

##@ 1. Développement et simulation (poste WSL)

help: ## Affiche cette aide
	@awk 'BEGIN {FS = ":.*##"} \
	  /^##@/ {printf "\n%s\n", substr($$0, 5)} \
	  /^[a-zA-Z0-9_%-]+:.*##/ {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "Variables : C=$(C) (mission)  IMG=$(IMG) (conteneur)  DRONE=$(DRONE)"

print-vars: ## Affiche les variables résolues (pour déboguer)
	@echo "C=$(C)  WS=$(WS)  IMG=$(IMG)  COMPOSE=$(COMPOSE)  DRONE=$(DRONE)  SITL_HOST=$(SITL_HOST)"

init: ## Après le clone : sous-modules, réglages git, dossiers ignorés. Sans risque à relancer.
	git submodule update --init --recursive
	git config submodule.recurse true
	git config push.recurseSubmodules on-demand
	mkdir -p models bags
	@echo "OK. Lance maintenant : make build C=gcs"

status: ## État de git et des sous-modules en une page
	@echo "Branche : $$(git branch --show-current)"
	@echo "Sous-modules (espace = à jour, + = commit différent du pointeur, - = non initialisé) :"
	@git submodule status
	@git status --short | head -20

check: ## Vérifie le dépôt (package.xml, liens, sous-modules, README). À lancer avant une PR.
	python3 scripts/check.py

models: ## Télécharge les modèles de vision dans models/ (hors git)
	@test -n "$(MODELS_URL)" || { echo "Renseigne MODELS_URL dans le Makefile (lien vers l'archive des modèles)."; exit 1; }
	mkdir -p models && curl -L "$(MODELS_URL)" | tar -xz -C models

build: ## Construit le workspace de C dans le conteneur IMG (colcon)
	docker compose -f $(COMPOSE) run --rm $(IMG) bash -lc \
	  'source /opt/ros/humble/setup.bash && cd /aeac/$(WS) && colcon build --symlink-install'

dev: ## Entre dans le conteneur de développement (tout le dépôt est monté dans /aeac)
	docker compose -f compose/dev.yml up -d dev
	docker compose -f compose/dev.yml exec dev bash

sim: ## Simulation de la mission C : mavros vers le SITL de Mission Planner + launch avec sim:=true
	docker compose -f compose/sim.yml up --abort-on-container-exit

shell: ## Second terminal dans le conteneur IMG déjà lancé (make shell IMG=sim pour les mocks)
	docker compose -f $(COMPOSE) exec $(IMG) bash

logs: ## Logs du conteneur IMG
	docker compose -f $(COMPOSE) logs -f

link: ## Lie un paquet partagé au workspace de C : make link C=water PKG=tools
	@test -n "$(PKG)" || { echo "Usage : make link C=<mission> PKG=<paquet de packages/>"; exit 1; }
	@test -d packages/$(PKG) || { echo "packages/$(PKG) n'existe pas"; exit 1; }
	cd $(WS)/src && ln -s ../../../packages/$(PKG) $(PKG)
	@echo "Lien créé : $(WS)/src/$(PKG). Pense à le commettre."

bag: ## Enregistre un rosbag daté dans bags/ (topics /aeac/* et mavros utiles), depuis le conteneur IMG
	docker compose -f $(COMPOSE) exec $(IMG) bash -lc \
	  'source /opt/ros/humble/setup.bash && ros2 bag record -o /aeac/bags/$$(date +%F_%H-%M) \
	   -e "/aeac/.*|/mavros/(state|rc/in|local_position/pose|global_position/global|battery)"'

##@ 2. Test sur véhicule (à la main, en avant-plan, Ctrl-C pour arrêter)

mavros: ## mavros vers le Pixhawk (Jetson)
	docker compose -f compose/mavros.yml up

zed: ## Caméra ZED (Jetson)
	docker compose -f compose/zed.yml up

zenoh-air: ## Pont Zenoh côté drone (Jetson)
	docker compose -f compose/zenoh-air.yml up

vision: ## Conteneur vision GPU (Jetson)
	docker compose -f compose/vision.yml up

drone: ## La mission C sur le drone (Jetson)
	docker compose -f compose/drone.yml up

gcs: ## Les nœuds sol de la mission C + pont Zenoh vers DRONE (portable)
	docker compose -f compose/gcs.yml -f compose/zenoh-ground.yml up

##@ 3. Déploiement (Jetson, systemd ; leads)

deploy: ## Installe les services systemd depuis systemd/ et fixe la mission C au boot
	sudo mkdir -p /etc/aeac
	echo "$(C)" | sudo tee /etc/aeac/mission > /dev/null
	for s in $(SERVICES); do sed "s#__REPO__#$(CURDIR)#g" systemd/$$s.service | sudo tee /etc/systemd/system/$$s.service > /dev/null; done
	sudo systemctl daemon-reload
	sudo systemctl enable --now $(SERVICES)
	@echo "Déployé. Mission au boot : $(C). Pour tester à la main : make undeploy puis make drone C=$(C)"

undeploy: ## Arrête et désactive tous les services (pour repasser en test à la main)
	sudo systemctl disable --now $(SERVICES) || true

%-status: ## État d'un service : make mavros-status, make mission-status, ...
	systemctl status $* --no-pager

%-logs: ## Logs d'un service en direct : make mission-logs
	journalctl -u $* -f

%-restart: ## Redémarre un service : make zenoh-air-restart
	sudo systemctl restart $*

bump: ## Avance un sous-module sur origin/main et prépare le commit : make bump PKG=tools
	@test -n "$(PKG)" || { echo "Usage : make bump PKG=<sous-module>"; exit 1; }
	git -C packages/$(PKG) fetch origin
	@echo "Commits gagnés :"; git -C packages/$(PKG) log --oneline HEAD..origin/main
	git -C packages/$(PKG) checkout --detach origin/main
	git -C packages/$(PKG) tag -f $(notdir $(CURDIR))-$$(date +%F)
	git add packages/$(PKG)
	@echo "Pointeur stagé. Commit avec : git commit -m 'bump $(PKG)'  puis  git push --recurse-submodules=on-demand"

.PHONY: help print-vars init status check models build dev sim shell logs link bag \
        mavros zed zenoh-air vision drone gcs deploy undeploy bump
