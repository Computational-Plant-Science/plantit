*Before getting to it...*

## What is PlantIT?

---

**PlantIT is web workflow automation for plant science.**

PlantIT aims to make reproducible research software easy to share and easy to use, guided by the following hypotheses:

- Most plant scientists and breeders have access to a web browser (when not in the field, at least).
- Most plant scientists and breeders do not care very much about software or infrastructure details.
- Many developers of plant science software are also plant scientists; see the previous bullet point.

## PlantIT **is not**:

---

- a workflow engine (e.g., [Snakemake](https://snakemake.readthedocs.io/en/stable/), [Nextflow](https://www.nextflow.io/), [Luigi](https://luigi.readthedocs.io/en/stable/), [Airflow](https://airflow.apache.org/))
- a distributed queue or task scheduler (e.g., [Celery](https://docs.celeryproject.org/en/stable/index.html) or [Dask](https://dask.org/), respectively)
- a batch processing, dataflow/streaming, or analytics framework (e.g., [Spark](https://spark.apache.org/))
- a container orchestrator (e.g., [Kubernetes](https://kubernetes.io/))
- a cluster resource manager (e.g., [Torque/Moab](https://adaptivecomputing.com/cherry-services/torque-resource-manager/), [Slurm](https://slurm.schedmd.com/overview.html))

PlantIT does not attempt to reinvent these tools or reproduce their features. *PlantIT simply glues them together in useful ways (we hope)*.

PlantIT is sort of like [Metaflow](https://metaflow.org/), minus the Python DSL, with a web application bolted on top. Metaflow's documentation [states](https://docs.metaflow.org/introduction/what-is-metaflow#infrastructure-stack-for-data-science):

```Internally, Metaflow leverages existing infrastructure when feasible... it is tightly integrated with Amazon Web Services. The core value proposition of Metaflow is its integrated full-stack, human-centric API, rather than reinvention of the stack itself.```

PlantIT embraces a similar philosophy; just substitute [Cyverse](https://www.cyverse.org)/HPC for AWS (though AWS integrations are planned).

Some preliminary notes for workflow developers:

- **PlantIT doesn't care what your workflow looks like**. If it runs in Docker or Singularity, it will run on PlantIT. Use any software stack you like.
- **PlantIT doesn't care what your data looks like**. If it fits in a file or directory on your deployment target, PlantIT will feed it to your workflow.