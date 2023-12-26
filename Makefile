# You can use .PHONY to tell make that we aren't building a target output file

SHELL := /bin/bash
UID := $(shell id -u)
GID := $(shell id -g)
# USER := $(USER)

test:
	@echo ${USER}

.PHONY: docker_install
docker_install:
	sudo curl -sSL https://get.docker.com | sh

.PHONY: docker_rootless
docker_rootless:
	sudo groupadd docker || true
	sudo usermod -aG docker ${USER} || true
	newgrp docker

.PHONY: docker_verify
docker_verify:
	# Verify rootless installation
	docker run hello-world

.PHONY: docker_compose
docker_compose:
	sudo apt-get update
	sudo apt-get install docker-compose-plugin

.PHONY: setup
setup:
	make docker_install
	make docker_rootless

.PHONY: run
run: # Runs the docker container with according environment variables
run:
	env UID=${UID} GID=${GID} docker compose -f docker-compose.yml up -d

.PHONY: stop
stop: # Runs the docker container with according environment variables
stop:
	env UID=${UID} GID=${GID} docker compose -f docker-compose.yml down

.PHONY: logs
logs: ## show the log output of the containers
logs:
	env UID=${UID} GID=${GID} docker compose logs

.PHONY: secret
secret: # create local secret
secret:
	echo "CREDENTIAL_FILE_KEY=$(shell gpg --gen-random --armor 1 18)" > .env.secret