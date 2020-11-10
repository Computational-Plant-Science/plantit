### Preliminaries

---

First, some basics:

- Because PlantIT supports deployments to shared computing environments (e.g., HPC clusters), PlantIT workflows are *containerized*: every workflow runs in one or more [Singularity](https://sylabs.io/singularity/) containers. We recommend getting familiar with containers in general and Singularity in particular before moving on.
- PlantIT doesn't care what your workflow looks like. If it runs in Docker or Singularity, it will run on PlantIT. Use any software stack you like.
- PlantIT doesn't care what your data looks like. If it fits in a file or directory on your deployment target, PlantIT will feed it to your workflow.

All you need to host your own workflows on PlantIT is a [GitHub](https://github.com/) account. Create one if you need to, otherwise you're ready to go!

<br>

### The `plantit.yaml` file

---

Hosting code on PlantIT is as easy as adding a `plantit.yaml` file to your GitHub repository. At its simplest, the file should look something like this:

```yaml
name: Hello Groot
author: Groot
public: True                  # should this workflow be visible to other users of PlantIT?
clone: False                  # should this workflow's repository be cloned to the deployment target before running?
image: docker://alpine        # the Docker or Singularity image your workflow's container(s) will be built from
commands: echo "I am Groot!"  # the commands to run inside your container(s)
```

Note that this flow definition does not specify resource requirements. PlantIT presently supports 3 deployment targets:
 
 - **Sandbox**: a light-weight container environment, good for test runs on very small datasets.
 - **Sapelo2**: the Georgia Advanced Computing Research Center's Sapelo2 cluster.
 - **Stampede2**: the Texas Advanced Computing Center's Stampede2 cluster.
 
In the **Sandbox** your code will run in a very resource-constrained environment. Please keep your runs small.

To deploy your code on clusters, you must add a `resources` section to your `plantit.yaml` file:

```yaml
resources:
    time: "01:00:00",
    mem: "1GB",
    tasks: 1,
    cores: 1
```

#### Parameters

To parametrize your workflow, add a `params` section. For example, to allow the user to configure the message printed by the trivial workflow above:

```yaml
name: Hello Who?
author: Groot
public: True
clone: False
image: docker://alpine
commands: echo "$MESSAGE"
params:
 - message
```

This will cause the value of `message`, specified by the user in the browser, to be substituted into the `command` at runtime.

#### Input/Output

PlantIT can automatically copy input files from the [CyVerse Data Store](https://www.cyverse.org/data-store) (or any other iRODS instance) onto the file system in your deployment environment, then push output files back to the store after your workflow runs. To enable this behavior, add `from` and `to` sections to your configuration.

The following workflow prints the contents of an input file and writes a message to an output file:

```yaml
name: Hello File
author: Groot
image: docker://alpine
public: True
clone: False
from: file
to: file
params:
  - message
commands: cat "$INPUT" && echo "$MESSAGE" >> "$OUTPUT"
```

PlantIT will prompt users of this workflow to select input and output paths in the browser. Note that this configuration maps a single input file to a single output file. If the user provides a directory containing multiple input files, PlantIT will automagically spawn multiple containers to process them in parallel. To indicate that your code accepts an entire *directory* as input (and should not be parallelized), use `from: directory` instead.
