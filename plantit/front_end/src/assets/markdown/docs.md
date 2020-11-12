### Preliminaries

---

First, some basics:

- Because PlantIT supports deployments to shared computing environments (e.g., HPC clusters), PlantIT workflows are *containerized*: code runs in one or more [Singularity](https://sylabs.io/singularity/) containers.
- PlantIT doesn't care what your code looks like. If it runs in Docker or Singularity, it will run on PlantIT. Use any stack you like.
- PlantIT doesn't care what your data looks like. If it fits in a file or directory on your deployment target, PlantIT will feed it to your code.

To deploy your own <i class="fas fa-stream fa-1x fa-fw"></i> **Flow**s on PlantIT, you'll need a [GitHub](https://github.com/) account.

<br>

### The `plantit.yaml` file

---

To host code (that is, a <i class="fas fa-stream fa-1x fa-fw"></i> **Flow**) on PlantIT, just add a `plantit.yaml` file to your GitHub repository. It should look something like this:

```yaml
name: Hello Groot
author: Groot
public: True                  # should this flow be visible to other users of PlantIT?
clone: False                  # should this workflow's repository be cloned to the deployment target before running?
image: docker://alpine        # the Docker or Singularity image your workflow's container(s) will be built from
commands: echo "I am Groot!"  # the commands to run inside your container(s)
```

Note that no resource requirements are specified. PlantIT supports 3 deployment targets:
 
 - **Sandbox**: a light-weight container environment, good for test runs on very small datasets.
 - **Sapelo2**: the Georgia Advanced Computing Research Center's Sapelo2 cluster.
 - **Stampede2**: the Texas Advanced Computing Center's Stampede2 cluster.
 
In the **Sandbox** your code will run in a very resource-constrained environment. Please keep your runs small (<1GB memory and disk space), and be aware that they will fail if the environment cannot service them.

To deploy your <i class="fas fa-stream fa-1x fa-fw"></i> **Flow** on one of the clusters, add a `resources` section to your `plantit.yaml` file. For example, to request 1 processor on 1 node and 1GB of memory for 1 hour:

```yaml
resources:
    time: "01:00:00",
    mem: "1GB",
    tasks: 1,
    cores: 1
```

Note that the **Stampede2** cluster is equipped with virtual memory (up to ?? GB), and will ignore `mem` values specified.

Note also that your runs will fail if they do not complete within the requested `time`, or if they exceed their memory allotment on **Sapelo2**.

#### Parameters

To parametrize your <i class="fas fa-stream fa-1x fa-fw"></i> **Flow**, add a `params` section. For example, to allow the user to configure the message printed by the trivial workflow above:

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

PlantIT can automatically copy input files from the [CyVerse Data Store](https://www.cyverse.org/data-store) onto the file system in your deployment environment, then push output files back to the Data Store after your code runs. To configure inputs and outputs for your <i class="fas fa-stream fa-1x fa-fw"></i> **Flow**, add `from` and `to` sections to your configuration.

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

PlantIT will prompt users of this <i class="fas fa-stream fa-1x fa-fw"></i> **Flow** to select input and output paths in the browser. Note that this configuration maps a single input file to a single output file. If the user provides a directory containing multiple input files, PlantIT will automagically spawn multiple containers, one for each input file. To indicate that your code accepts an entire *directory* as input (and should not be parallelized), use `from: directory` instead.
