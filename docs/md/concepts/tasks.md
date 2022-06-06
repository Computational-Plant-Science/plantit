# <i class="fas fa-tasks fa-1x fa-fw"></i> **Tasks**

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Task monitoring](#task-monitoring)
- [Task lifecycle](#task-lifecycle)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

A <i class="fas fa-tasks fa-1x fa-fw"></i> **Task** is a single instance of a workflow. When a task is submitted from the browser, the `plantit` web app hands it to an internal queue feeding a background worker. When the worker picks up the task, a job script is generated and submitted to the selected cluster/supercomputer scheduler. The task lifecycle is a simple state machine strung together from Celery tasks.

## Task monitoring

For a tutorial on monitoring a task and retrieving results, see the [quickstart](../introduction/quickstart.md).

## Task lifecycle

The task lifecycle is a state machine progressing from `CREATED` to `RUNNING` to one of several mutually exclusive final states (`COMPLETED`,  `FAILED`, `TIMEOUT`, or `CANCELLED`).

![Task Lifecycle](../../media/lifecycle.jpg)

When a task successfully completes, results are automatically transferred to the selected location in the CyVerse data store. The user is then shown results produced and may download them from the browser individually or bundled into a single archive.
