# Contributions

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Configuring a development environment](#configuring-a-development-environment)
- [Command cheatsheet](#command-cheatsheet)
  - [Docker Compose](#docker-compose)
  - [Docker](#docker)
  - [Django](#django)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

We welcome contributions to the `plantit` codebase, from [bug reports](https://github.com/Computational-Plant-Science/plantit/issues/new) to documentation fixes to pull requests of all kinds! All development planning is carried out on GitHub: see the [Changelog/Roadmap](https://github.com/Computational-Plant-Science/plantit/wiki/Changelog-&-Roadmap) and [Issues](https://github.com/Computational-Plant-Science/plantit/issues) in particular.

## Configuring a development environment

See the [README](https://github.com/Computational-Plant-Science/plantit) for instructions on installing the project from source.

## Command cheatsheet

Below is a list of handy commands for managing the `plantit` application.

### Docker Compose

- `docker-compose -f docker-compose.dev.yml up`: bring the full application (all containers) up
- `docker-compose -f docker-compose.dev.yml down`: bring the full application (all containers) down
- `docker-compose -f docker-compose.dev.yml run plantit <command>` run a command in the `plantit` container (starting containers as needed)
- `docker-compose -f docker-compose.dev.yml exec plantit <command>` run a command in the `plantit` container (assumes all containers are up)

### Docker

- `docker ps`: list running containers
- `docker exec -it <container ID> bash`:  enter an already running container

### Django

- `./manage.py`: list Django commands
- `./manage.py makemigrations`: create plan for django migrations
- `./manage.py migrate`: run django migrations
- `./manage.py shell`: opens Django Python interpreter

