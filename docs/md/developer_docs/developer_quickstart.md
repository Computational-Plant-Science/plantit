<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Developer Quickstart](#developer-quickstart)
  - [Preliminaries](#preliminaries)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Developer Quickstart

## Preliminaries

First, some basics:

- Because PlantIT supports deployments to shared computing environments (e.g., HPC clusters), PlantIT workflows are *containerized*: code runs in one or more [Singularity](https://sylabs.io/singularity/) containers.
- PlantIT doesn't care what your code looks like. If it runs in Docker or Singularity, it will run on PlantIT. Use any stack you like.
- PlantIT doesn't care what your data looks like. If it fits in a file or directory on your deployment target, PlantIT will feed it to your code.

To deploy your own <i class="fas fa-stream fa-1x fa-fw"></i> **Flow**s on PlantIT, you'll need a [GitHub](https://github.com/) account.

<br>

