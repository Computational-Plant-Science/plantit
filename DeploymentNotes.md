- PlantIT code saved in /opt/PlantIT

# ufw and docker

## Blocking connection to repository
This is an ongoing issue

## Ip Tables
Docker will modify the iptables, allowing ports that
should be blocked by the firewall ufw to be available publicly.
I added `DOCKER_OPTS="--iptables=false"` to `/etc/default/docker`
to stop docker from editing the iptables.

Any ports that should be available publicly from docker must
be allowed in ufw.
