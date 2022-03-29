<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [User Quickstart](#user-quickstart)
- [Workflow](#workflow)
- [Task](#task)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Quickstart

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

A <i class="fas fa-database fa-1x fa-fw"></i> **Dataset** is a collection of data objects in the CyVerse data store. 

##### Workflows

A <i class="fas fa-stream fa-1x fa-fw"></i> **Workflow** is an executable research application packaged into a [Docker](https://www.docker.com/) image. Workflows execute in a [Singularity](https://sylabs.io/singularity/) container runtime.

##### Tasks

A <i class="fas fa-tasks fa-1x fa-fw"></i> **Task** is a single instance of a workflow. When a task is submitted from the browser, the `plantit` web app hands it to an internal queue feeding a background worker. When the worker picks up the task, a job script is generated and submitted to the selected cluster/supercomputer scheduler. The task lifecycle is a simple state machine strung together from Celery tasks.

![Task Lifecycle](../../media/task.jpg)

When a task successfully completes, results are automatically transferred to the selected location in the CyVerse data store. The user is then shown results produced and may download them from the browser individually or bundled into a single archive.