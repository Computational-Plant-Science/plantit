<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Preliminaries](#preliminaries)
- [The `plantit.yaml` file](#the-plantityaml-file)
  - [Parameters](#parameters)
  - [Input/Output](#inputoutput)
    - [Workflow "shapes"](#workflow-shapes)
  - [Test Dataset](#test-dataset)
  - [Publication DOI](#publication-doi)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

### Preliminaries

---

Before we start, a few basics:

- Because PlantIT supports deployments to shared computing environments (e.g., HPC clusters), PlantIT workflows are *containerized*: every workflow runs in one or more [Singularity](https://sylabs.io/singularity/) containers. We recommend getting familiar with containers in general and Singularity in particular before moving on.
- PlantIT doesn't care what your workflow looks like. If it runs in Docker or Singularity, it will run on PlantIT. Use any software stack you like.
- PlantIT doesn't care what your data looks like. If it fits in a file or directory on your deployment target, PlantIT will feed it to your workflow.

All you need to host your own workflows on PlantIT is a [GitHub](https://github.com/) account. Create one if you need to, otherwise you're ready to go!

<br>

### The `plantit.yaml` file

---

Hosting a workflow on PlantIT is as easy as adding a `plantit.yaml` file to your repository. At its simplest, the file should look something like this:

```yaml
name: Hello Groot
author: Groot
public: True
clone: False
image: docker://alpine
commands: echo "I am Groot!"
```

The workflow's `name` and `author` are self-explanatory. Let's walk through the rest of the settings:

- `public`: should this workflow be visible to other users of PlantIT?
- `clone`: should this workflow's repository be cloned to the deployment target before running?
- `image`: the Docker or Singularity image your workflow's container(s) will be built from
- `commands`: the commands to run inside your container(s)

For more complex workflows, you'll want to add a few more sections to your `plantit.yaml`.

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

##### Workflow "shapes"

The following workflow prints the contents of an input file and writes a message to an ouput file:

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

PlantIT will prompt users of this workflow to select input and ouput paths in the browser. Note that this configuration maps a single input file to a single output file. If the user provides a directory containing multiple input files, PlantIT will automagically spawn multiple containers to process them in parallel. To indicate that your code accepts an entire *directory* as input (and should not be parallelized), use `from: directory` instead.

#### Test Dataset

This section is under construction.

#### Publication DOI

If you've published your algorithm or workflow, you can link PlantIT users to your publication with a `doi` attribute:

```yaml
doi: https://doi.org/10.1186/s13007-015-0093-3
```

The link will then be displayed in the browser.

