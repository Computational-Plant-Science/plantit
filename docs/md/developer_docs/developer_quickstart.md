# Developer Quickstart

## Preliminaries

First, some basics:

- Because PlantIT supports deployments to shared computing environments (e.g., HPC clusters), PlantIT workflows are *containerized*: code runs in one or more [Singularity](https://sylabs.io/singularity/) containers.
- PlantIT doesn't care what your code looks like. If it runs in Docker or Singularity, it will run on PlantIT. Use any stack you like.
- PlantIT doesn't care what your data looks like. If it fits in a file or directory on your deployment target, PlantIT will feed it to your code.

To deploy your own <i class="fas fa-stream fa-1x fa-fw"></i> **Flow**s on PlantIT, you'll need a [GitHub](https://github.com/) account.

<br>

