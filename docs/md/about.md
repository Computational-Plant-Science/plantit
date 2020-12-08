### This website...

---

- is a science gateway for plant phenomics and morphology
- was preceded by &mdash; grew out of, as it were &mdash; [DIRT](http://dirt.cyverse.org/?q=welcome) (**D**igital **I**maging of **R**oot **T**raits), which measures traits of monocot and dicot roots from digital images, automates the extraction of root traits, and makes high-throughput grid computing environments available to end-users without technical training
- is software-as-a-service allowing plant scientists and professionals to store, publish, and access data with CyVerse, and run simulations and analyses on clusters from a web browser
- is a platform-as-a-service for programmers and research software developers, integrated tightly with GitHub: just add a `plantit.yaml` file to your repository to deploy a workflow developed with your tools of choice

<br/>

### Why does it exist? 

---

When

- a field biologist collects a dataset, associates it with metadata, preprocesses it, acquires a DOI, and publishes it to the community
- a breeder deploys an automated imaging mechanism and generates thousands of 3D reconstructions, each described by hundreds of images
- a researcher develops a growth model and runs embarrassingly parallel simulations to explore the corresponding phenotype space
- a computer scientist shares an algorithm with biologists who may be unfamiliar with the command line and may use a variety of operating systems

...it can involve

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

It's flexible enough to run nearly any container-friendly workload, but if you want to do genomics, a tool like [CoGe](https://genomevolution.org/CoGe/) or [easyGWAS](https://easygwas.ethz.ch/) may be a better fit.

<br/>
 
### Is it a...

---

- pipeline framework (e.g., [Snakemake](https://snakemake.readthedocs.io/en/stable/), [Nextflow](https://www.nextflow.io/), [Luigi](https://luigi.readthedocs.io/en/stable/), [Airflow](https://airflow.apache.org/), [Metaflow](https://metaflow.org/))?
- distributed queue or task scheduler (e.g., [Celery](https://docs.celeryproject.org/en/stable/index.html) or [Dask](https://dask.org/))?
- batch processing, streaming, or analytics platform (e.g., map-reduce or [Spark](https://spark.apache.org/))?
- container orchestrator (e.g., [Kubernetes](https://kubernetes.io/))?
- cluster resource manager (e.g., [Torque/Moab](https://adaptivecomputing.com/cherry-services/torque-resource-manager/), [Slurm](https://slurm.schedmd.com/overview.html))?

No. It just tries to glue these things together in useful ways.

