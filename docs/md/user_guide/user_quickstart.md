<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [User Quickstart](#user-quickstart)
        - [Workflow](#workflow)
        - [Submission](#submission)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Quickstart

PlantIT has a few fundamental abstractions:

- <i class="fas fa-stream fa-1x fa-fw"></i> **Workflow**
- <i class="fas fa-tasks fa-1x fa-fw"></i> **Submission**

##### Workflow

A <i class="fas fa-stream fa-1x fa-fw"></i> **Workflow** is an executable, packaged neatly for deployment to a server, cluster, or supercomputer. Workflows execute in a container runtime. PlantIT doesn't much care what your workflow does. If it will run in [Docker](https://www.docker.com/) or [Singularity](https://sylabs.io/singularity/), it will most likely run on PlantIT.

##### Submission

A <i class="fas fa-tasks fa-1x fa-fw"></i> **Submission** is a single instance of a workflow.
