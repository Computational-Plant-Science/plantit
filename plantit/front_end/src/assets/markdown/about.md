### Prior art

---

- [DIRT](http://dirt.cyverse.org/?q=welcome): Digital Imaging of Root Traits measures traits of monocot and dicot roots from digital images. DIRT automates the extraction of root traits by making high-throughput grid computing environments available to end-users without technical training.

<br>

### Why does PlantIT exist? 

---

Some principles:

- Computational science should be simple to conduct and straightforward to reproduce.
- Research software should be easy to version, share, configure, deploy, and monitor.

Some hypotheses:

- Most plant scientists have access to a modern web browser (when not in the field, at least).
- Most plant scientists do not want to care very much about computing infrastructure details.
- Many developers of plant science research software are also plant scientists; see previous.

Some vignettes:

- An experimentalist collects a dataset, associates it with metadata, preprocesses it, acquires a DOI, publishes it, and attempts to encourage replication.
- A researcher develops a growth model and runs a series of embarrassingly parallel Monte Carlo simulations to explore the corresponding phenotype space.
- A breeder deploys an automated imaging mechanism and generates 3D reconstructions of thousands of individuals, each described by hundreds of images.
- A computer scientist shares an algorithm with a biologist who is unfamiliar with the command line and would like to use it on a variety of operating systems.

Typically, these tasks might involve:

- hard drives
- shell scripting
- emailing strangers
- juggling job submission scripts
- sticking Post-it notes to computer monitors
- trying to remember which directory yesterday's data is in
- answering support requests at 2 A.M. ("Why doesn't it work on my machine?")

Couldn't we just do these things in the browser? That would be nice.

<br>

### Is PlantIT a bioinformatics gateway?

---

Sort of. PlantIT is flexible enough to run nearly any HPC workflow, but the platform is tailored for *phenomics*. If you're looking to do genomics, a different tool such as [CoGe](https://genomevolution.org/CoGe/) or [easyGWAS](https://easygwas.ethz.ch/) is likely a better fit.

<br>
 
### Do we really need another workflow management system?

---

PlantIT is not:

- a workflow engine (e.g., [Snakemake](https://snakemake.readthedocs.io/en/stable/), [Nextflow](https://www.nextflow.io/), [Luigi](https://luigi.readthedocs.io/en/stable/), [Airflow](https://airflow.apache.org/))
- a distributed queue or task scheduler (e.g., [Celery](https://docs.celeryproject.org/en/stable/index.html) or [Dask](https://dask.org/), respectively)
- a batch processing, dataflow/streaming, or analytics framework (e.g., [Spark](https://spark.apache.org/))
- a container orchestrator (e.g., [Kubernetes](https://kubernetes.io/))
- a cluster resource manager (e.g., [Torque/Moab](https://adaptivecomputing.com/cherry-services/torque-resource-manager/), [Slurm](https://slurm.schedmd.com/overview.html))

PlantIT does not reinvent these tools or reproduce their features. *PlantIT just glues them together.*

PlantIT is a bit like [Metaflow](https://metaflow.org/) tuned for plant science workloads, minus the Python DSL, with a web application bolted on top. Metaflow's documentation [states](https://docs.metaflow.org/introduction/what-is-metaflow#infrastructure-stack-for-data-science):

```Internally, Metaflow leverages existing infrastructure when feasible... it is tightly integrated with Amazon Web Services. The core value proposition of Metaflow is its integrated full-stack, human-centric API, rather than reinvention of the stack itself.```

PlantIT embraces a similar philosophy; just substitute [Cyverse](https://www.cyverse.org)/HPC for AWS.
