# Installation

The all processes are contained within docker containers, the full website can be run using docker-compose from the root of the repository:

```bash
dev/reset.sh #Initialize databases and some other default values
docker-compose up
```

reset.sh adds the __user__: _admin_ with __password:__ _admin_

# Resetting an installation
```bash
sudo dev/reset.#!/bin/sh
```

dev/reset.sh can also be used to resets everything back to a "Fresh" install. Running dev/reset.sh does the following:

   - rebuilds all docker images
   - deletes all docker volumes
   - removes all Django migrations

then it

   - rebuilds the images
   - runs initial Django migration
   - creates an admin user
      - gives admin user file access permissions to ./django/files
   - adds test cluster

sudo is required to remove files added to ./django/files by the webserver.
