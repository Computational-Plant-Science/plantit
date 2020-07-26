### Prior art

---

PlantIT was preceded by &mdash; grew out of, as it were &mdash; [DIRT](http://dirt.cyverse.org/?q=welcome). **D**igital **I**maging of **R**oot **T**raits measures traits of monocot and dicot roots from digital images. DIRT automates the extraction of root traits by making high-throughput grid computing environments available to end-users without technical training.

<br>

### Why does PlantIT exist? 

---

Some ideas:

- computational science ought to be straightforward to reproduce
- research software ought to be easy to version, run, and share

Some vignettes:

- a field biologist collects a dataset, associates it with metadata, preprocesses it, acquires a DOI, and publishes it to the community
- a breeder deploys an automated imaging mechanism and generates thousands of 3D reconstructions, each described by hundreds of images
- a researcher develops a growth model and runs embarrassingly parallel Monte Carlo simulations to explore the corresponding phenotype space
- a computer scientist shares an algorithm with biologists who may be unfamiliar with the command line and may use a variety of operating systems

These may involve:

- hard drives
- shell scripting
- emailing strangers
- juggling job submission scripts
- answering support requests at 2 A.M.
- sticking Post-it notes to computer monitors
- trying to remember which directory yesterday's data is in

PlantIT makes the computer do some of the painful bits.

<br>

### With PlantIT, you can...

---

- access your data
- upload your data
- acquire a DOI for and publish your data
- associate metadata with your data
- access public datasets
- automatically feed your data to a workflow
- containerize your workflow
- run your workflow
- run a public workflow
- collaborate on workflows and data
- develop and share a new workflow
- download the results of your workflow
- automatically push workflow results to a data store
- trigger a workflow to run when your code or data changes
- *think less about infrastructure and more about science*

<br>

### Is PlantIT a bioinformatics gateway?

---

Sort of. PlantIT is flexible enough to run nearly any container-friendly code, but is intended for and suited to phenomics workloads. If you want to do genomics, a tool like [CoGe](https://genomevolution.org/CoGe/) or [easyGWAS](https://easygwas.ethz.ch/) may be a better fit.

<br>
 
### Is PlantIT a workflow management system?

---

PlantIT is not:

- a workflow engine (e.g., [Snakemake](https://snakemake.readthedocs.io/en/stable/), [Nextflow](https://www.nextflow.io/), [Luigi](https://luigi.readthedocs.io/en/stable/), [Airflow](https://airflow.apache.org/))
- a distributed queue or task scheduler (e.g., [Celery](https://docs.celeryproject.org/en/stable/index.html) or [Dask](https://dask.org/), respectively)
- a batch processing, dataflow/streaming, or analytics framework (e.g., [Spark](https://spark.apache.org/))
- a container orchestrator (e.g., [Kubernetes](https://kubernetes.io/))
- a cluster resource manager (e.g., [Torque/Moab](https://adaptivecomputing.com/cherry-services/torque-resource-manager/), [Slurm](https://slurm.schedmd.com/overview.html))

PlantIT is a bit like [Metaflow](https://metaflow.org/) tuned for plant phenomics, minus the Python DSL, with a web application bolted on top. Metaflow's documentation [states](https://docs.metaflow.org/introduction/what-is-metaflow#infrastructure-stack-for-data-science):

```Internally, Metaflow leverages existing infrastructure when feasible... it is tightly integrated with Amazon Web Services. The core value proposition of Metaflow is its integrated full-stack, human-centric API, rather than reinvention of the stack itself.```

PlantIT embraces a similar philosophy; just substitute [Cyverse](https://www.cyverse.org)/[Github](https://www.github.com/)/HPC for AWS. PlantIT is about *integrations*: it just glues stuff together in useful ways.
