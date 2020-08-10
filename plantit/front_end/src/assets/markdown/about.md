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

- access public datasets
- access or upload your own datasets
- associate metadata with your datasets
- acquire a DOI for and publish your datasets
- deploy a workflow to a HPC/HTC cluster
- download workflow results
- upload workflow results as a new dataset
- trigger a workflow to run when it or your dataset changes
- develop a new workflow
- publish workflows to the community
- **think less about infrastructure and more about science**

<br>

### Is PlantIT a bioinformatics gateway?

---

Sort of. PlantIT is a browser-based data science portal for plant phenomics. PlantIT is flexible enough to run nearly any container-friendly workload, but if you want to do genomics, a tool like [CoGe](https://genomevolution.org/CoGe/) or [easyGWAS](https://easygwas.ethz.ch/) may be a better fit.

<br>
 
### PlantIT is not a...

---

- computational pipeline framework (e.g., [Snakemake](https://snakemake.readthedocs.io/en/stable/), [Nextflow](https://www.nextflow.io/), [Luigi](https://luigi.readthedocs.io/en/stable/), [Airflow](https://airflow.apache.org/), [Metaflow](https://metaflow.org/))
- distributed queue or task scheduler (e.g., [Celery](https://docs.celeryproject.org/en/stable/index.html) or [Dask](https://dask.org/), respectively)
- batch processing, dataflow/streaming, or analytics framework (e.g., [Spark](https://spark.apache.org/))
- container orchestrator (e.g., [Kubernetes](https://kubernetes.io/))
- cluster resource manager (e.g., [Torque/Moab](https://adaptivecomputing.com/cherry-services/torque-resource-manager/), [Slurm](https://slurm.schedmd.com/overview.html))

