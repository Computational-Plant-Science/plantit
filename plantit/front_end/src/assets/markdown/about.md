### What is plantit?

---

- a web workflow automation platform for plant phenomics: a science gateway for both data and software
- preceded by &mdash; grew out of, as it were &mdash; [DIRT](http://dirt.cyverse.org/?q=welcome) (**D**igital **I**maging of **R**oot **T**raits), which measures traits of monocot and dicot roots from digital images, automates the extraction of root traits, and makes high-throughput grid computing environments available to end-users without technical training
- software-as-a-service allowing plant scientists and professionals to store, publish, and access data with CyVerse, and run simulations and analyses on clusters from a web browser
- a platform-as-a-service for programmers and research software developers, integrated tightly with GitHub: just add a `plantit.yaml` file to your repository to deploy a workflow developed with your tools of choice &mdash; if it runs in Docker or Singularity, it will run on PlantIT

<br/>

### Why does it exist? 

---

Imagine:

- a field biologist collects a dataset, associates it with metadata, preprocesses it, acquires a DOI, and publishes it to the community
- a breeder deploys an automated imaging mechanism and generates thousands of 3D reconstructions, each described by hundreds of images
- a researcher develops a growth model and runs embarrassingly parallel simulations to explore the corresponding phenotype space
- a computer scientist shares an algorithm with biologists who may be unfamiliar with the command line and may use a variety of operating systems

These tasks can involve annoying sub-tasks:

- hard drives
- shell scripting
- emailing strangers
- juggling job submission scripts
- answering support requests at 2am
- sticking notes to computer monitors
- remembering which directory yesterday's data is in

Can't the computer do some of the painful bits?

### Is it a bioinformatics gateway?

---

It's flexible enough to run nearly any container-friendly workload, but if you want to do genomics, a tool like [CoGe](https://genomevolution.org/CoGe/) or [easyGWAS](https://easygwas.ethz.ch/) may be a better fit

<br/>
 
### Is it a...

---

- computational pipeline framework (e.g., [Snakemake](https://snakemake.readthedocs.io/en/stable/), [Nextflow](https://www.nextflow.io/), [Luigi](https://luigi.readthedocs.io/en/stable/), [Airflow](https://airflow.apache.org/), [Metaflow](https://metaflow.org/))? No.
- distributed queue or task scheduler (e.g., [Celery](https://docs.celeryproject.org/en/stable/index.html) or [Dask](https://dask.org/), respectively)? No.
- batch processing, dataflow/streaming, or analytics framework (e.g., [Spark](https://spark.apache.org/))? No.
- container orchestrator (e.g., [Kubernetes](https://kubernetes.io/))? No.
- cluster resource manager (e.g., [Torque/Moab](https://adaptivecomputing.com/cherry-services/torque-resource-manager/), [Slurm](https://slurm.schedmd.com/overview.html))? No.

It's none of these things. It just tries to glue them together in helpful ways.

