# Quickstart

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Conceptual model](#conceptual-model)
  - [Datasets](#datasets)
  - [Workflows](#workflows)
  - [Tasks](#tasks)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

`plantit` is designed to support two broadly defined use cases, corresponding to user groups with different concerns and priorities.

- researchers: analyzing data, running models & simulations
- developers: publishing and maintaining research software

## Conceptual model

`plantit` has a few fundamental abstractions:

- <i class="fas fa-database fa-1x fa-fw"></i> **Dataset**
- <i class="fas fa-stream fa-1x fa-fw"></i> **Workflow**
- <i class="fas fa-tasks fa-1x fa-fw"></i> **Task**

A <i class="fas fa-database fa-1x fa-fw"></i> **Dataset** is a set of data objects. A <i class="fas fa-stream fa-1x fa-fw"></i> **Workflow** is a containerized research application. A workflow *must* yield a dataset as output and *may* accept one as input (workflows should be designed as functions or generators, *not* for their side effects &mdash; ideally, they should have none). An instantiation of a workflow is called a <i class="fas fa-tasks fa-1x fa-fw"></i> **Task**. 

### Datasets

A <i class="fas fa-database fa-1x fa-fw"></i> [**Dataset**](datasets.md) is a collection of data objects in the CyVerse data store. 

### Agents

An <i class="fas fa-server fa-1x fa-fw"></i> [**Agent**](agents.md) is a deployment target: an abstraction of a cluster or supercomputer along with SLURM scheduler configuration details.

### Workflows

A <i class="fas fa-stream fa-1x fa-fw"></i> [**Workflow**](workflows.md) is an executable research application packaged into a [Docker](https://www.docker.com/) image. Workflows execute in a [Singularity](https://sylabs.io/singularity/) container runtime. To define a workflow, [add a `plantit.yaml` file to any public GitHub repository](workflows.md).

### Tasks

A <i class="fas fa-tasks fa-1x fa-fw"></i> [**Task**](tasks.md) is an instance of a workflow, deployed to an agent. When a task is submitted from the browser, the `plantit` web app hands it to an internal queue feeding a background worker. When the worker picks up the task, a job script is generated and submitted to the selected cluster/supercomputer scheduler. The task lifecycle is a simple state machine strung together from Celery tasks.
