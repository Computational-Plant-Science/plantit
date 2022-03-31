# About `plantit`

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [What is it?](#what-is-it)
- [What isn't it?](#what-isnt-it)
- [What can I use it for?](#what-can-i-use-it-for)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## What is it?

`plantit` is a workflow automation tool for computational plant science. It is simultaneously *software-as-a-service* for researchers and a *platform-as-a-service* for programmers & developers.

- *SaaS*: store, publish, and access data with CyVerse, run (possibly highly parallel) simulations and analyses from a browser
- *Paas*: built on GitHub and Docker, add a `plantit.yaml` file to GitHub repository to deploy Docker images as Singularity containers on clusters or supercomputers

![](../media/p1.png)

## What isn't it?

`plantit` is none of the following (although it tries to glue these systems together in helpful ways).

- a pipeline orchestrator (e.g., [Snakemake](https://snakemake.readthedocs.io/en/stable/), [Nextflow](https://www.nextflow.io/), [Luigi](https://luigi.readthedocs.io/en/stable/), [Airflow](https://airflow.apache.org/), [Metaflow](https://metaflow.org/))
- a distributed queue or task scheduler (e.g., [Celery](https://docs.celeryproject.org/en/stable/index.html) or [Dask](https://dask.org/))
- a batch processing, streaming, or analytics platform (e.g., map-reduce or [Spark](https://spark.apache.org/))
- a container automation system (e.g., [Kubernetes](https://kubernetes.io/))
- a cluster scheduler (e.g., [Torque/Moab](https://adaptivecomputing.com/cherry-services/torque-resource-manager/), [Slurm](https://slurm.schedmd.com/overview.html))

![](../media/p2.png)

## What can I use it for?

PlantIT is flexible enough to run most container-friendly workloads, but if you want to do genomics, an established tool like [CoGe](https://genomevolution.org/CoGe/) or [easyGWAS](https://easygwas.ethz.ch/) may be a better fit. Feel free to [get in touch](https://github.com/Computational-Plant-Science/plantit/discussions) with questions about your use case.
