## What **is** PlantIT, exactly?

---

**PlantIT is web workflow automation for plant scientists.**

PlantIT aims to make reproducible research software easy to share and easy to use. PlantIT is guided by the following hypotheses:

- Most plant scientists have access to the web and a modern browser (when not in the field, at least).
- Most plant scientists do not care about infrastructure details. Plant scientists care about research.
- Many developers of plant science software are also plant scientists; see the previous bullet point.
- Most developers of plant science software are familiar with `git` (and likely have a Github account).

Too much good software sits undiscovered and idle, collecting digital dust, after the project is completed or paper published. PlantIT aims to change that.

## PlantIT **is not**:

---

- a workflow engine (e.g., [Snakemake](https://snakemake.readthedocs.io/en/stable/), [Nextflow](https://www.nextflow.io/), [Luigi](https://luigi.readthedocs.io/en/stable/), [Airflow](https://airflow.apache.org/))
- a distributed queue or task scheduler (e.g., [Celery](https://docs.celeryproject.org/en/stable/index.html) or [Dask](https://dask.org/), respectively)
- a batch processing, dataflow/streaming, or analytics framework (e.g., [Spark](https://spark.apache.org/))
- a container orchestrator (e.g., [Kubernetes](https://kubernetes.io/))
- a cluster resource manager (e.g., [Torque/Moab](https://adaptivecomputing.com/cherry-services/torque-resource-manager/), [Slurm](https://slurm.schedmd.com/overview.html))

PlantIT uses a number of these technologies internally, but does not reinvent them. *PlantIT simply glues them together in useful ways*.

PlantIT is kind of like [Metaflow](https://metaflow.org/), minus the Python DSL, with a web application bolted on top. Metaflow's documentation [states](https://docs.metaflow.org/introduction/what-is-metaflow#infrastructure-stack-for-data-science):


```Internally, Metaflow leverages existing infrastructure when feasible. In particular, it is tightly integrated with Amazon Web Services. The core value proposition of Metaflow is its integrated full-stack, human-centric API, rather than reinvention of the stack itself.```


PlantIT adopts a similar philosophy; just substitute Cyverse/HPC for AWS.

Some preliminary notes for workflow developers:

- PlantIT doesn't care what your workflow looks like. If it runs in Docker or Singularity, it will run on PlantIT. You can use any software stack you like.
- PlantIT doesn't care what your data looks like either. If it fits in a file or directory on your deployment target, PlantIT will feed it to your workflow.