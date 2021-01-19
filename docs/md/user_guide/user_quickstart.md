<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [User Quickstart](#user-quickstart)
        - [Flow](#flow)
        - [Run](#run)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Quickstart

PlantIT has 2 fundamental abstractions: <i class="fas fa-stream fa-1x fa-fw"></i> **Flow** and <i class="fas fa-terminal fa-1x fa-fw"></i> **Run**.

##### Flow

The **flow** is PlantIT's unit of work. PlantIT doesn't much care what it looks like. If it will run in [Docker](https://www.docker.com/) or [Singularity](https://sylabs.io/singularity/), it will run on PlantIT.

##### Run

A **run** is a single instantiation of a flow &mdash; a deployment to an HPC cluster, for instance.
