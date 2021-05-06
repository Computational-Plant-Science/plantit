<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Defining Workflows](#defining-workflows)
  - [The `plantit.yaml` file](#the-plantityaml-file)
    - [Deployment target resources](#deployment-target-resources)
        - [GPU mode](#gpu-mode)
      - [Timeouts and other errors](#timeouts-and-other-errors)
    - [Parameters](#parameters)
      - [Default values](#default-values)
    - [Workflow input/output](#workflow-inputoutput)
      - [Workflow input](#workflow-input)
        - [Input types (`file`, `files`, and `directory`)](#input-types-file-files-and-directory)
        - [Input filetypes](#input-filetypes)
      - [Workflow output](#workflow-output)
      - [A super simple example](#a-super-simple-example)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Defining Workflows

## The `plantit.yaml` file

To host code (that is, a **Workflow**) on PlantIT, just add a `plantit.yaml` file to your GitHub repository. It should look something like this:

```yaml
name: Hello Groot
author: Groot
public: True                  # should this workflow be visible to other users of PlantIT?
clone: False                  # should this workflow's repository be cloned to the deployment target before running?
image: docker://alpine        # the Docker or Singularity image your workflow's container(s) will be built from
commands: echo "I am Groot!"  # the commands to run inside your container(s)
```

### Deployment target resources

To make sure your **Workflow** can take full advantage of the resources made available by cluster or supercomputer schedulers, add a `resources` section to your `plantit.yaml` file. For example, to indicate that an instance of your workflow should request 1 process and 1 core on 1 node with 1GB of memory for 1 hour:

```yaml
resources:
  time: "01:00:00"
  mem: "1GB"
  processes: 1
  cores: 1
```

Note that some deployment targets may be equipped with virtual memory and ignore specified `mem` values.

##### GPU mode

To indicate that your workflow can take advantage of GPUs (only available on select deployment targets) add a `gpu: True` line to your configuration file. The environment variable `GPU_MODE` will be set to `true` in your workflow's runtime environment if the workflow is deployed to a cluster with GPU support; otherwise `GPU_MODE` will be `false`.

#### Timeouts and other errors

Workflows may fail if they do not complete within the requested `time`, if they exceed their memory allotment, or for a variety of reasons. Errors may be difficult to debug from the PlantIT web interface. Be sure to test workflows manually on any intended deployment target prior to deploying with PlantIT.

### Parameters

To parametrize your **Workflow**, add a `params` section. For example, to allow the user to configure the message printed by the trivial workflow above:

```yaml
name: Hello Who?
author: Groot
public: True
clone: False
image: docker://alpine
commands: echo "$MESSAGE"
params:
 - name: message
   type: string
```

This will cause the value of `message`, specified by the user in the browser, to be substituted into the `command` at runtime.

Note that PlantIT parameters are explicitly typed. The following parameter types are supported:

- `string`
- `select`
- `number`
- `boolean`

For example, a workflow with one of each parameter type might have the following `params` section:

```yaml
...
params:
  - name: String
    type: string
    default: Hello, world!
  - name: Select
    type: select
    options:
      - Option 1
      - Option 2
    default: Option 1
  - name: Number
    type: number
    default: 42
    step: 1
    min: 0
    max: 100
  - name: Boolean
    type: boolean
    default: False
```

#### Default values

To provide default values for your workflow's parameters, you can use a `default` attribute (see above).

### Workflow input/output

PlantIT can automatically copy input files from the [CyVerse Data Store](https://www.cyverse.org/data-store) onto the file system in your deployment environment, then push output files back to the Data Store after your code runs. To configure inputs and outputs for your **Workflow**, add `from` and `to` attributes to your configuration.

#### Workflow input

If your workflow requires inputs, add an `input` section to your configuration file, containing at minimum a `path` attribute (pointing either to a directory- or file-path in the CyVerse Data Store or Data Commons, or left blank) and a `kind` attribute indicating whether this workflow operates on a single `file`, multiple `files`, or an entire `directory`. For example:

##### Input types (`file`, `files`, and `directory`)

To indicate that your workflow should pull a single file from the Data Store and spawn a single container to process it, use `kind: file`. To pull a directory from the Data Store and spawn a container for each file, use `kind: files`. To pull a directory and spawn a single container to process it, use `kind: directory`.

It's generally a good idea for `path` to reference a community-released or curated public dataset in the CyVerse Data Commons, so prospective users can test your workflow on real data. For instance, a simple workflow which operates on a single file:

```yaml
input:
  path: /iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt
  kind: file
```

##### Input filetypes

To specify which filetypes your workflow is permitted to accept, add a `filetypes` attribute to the `input` section:

```yaml
input:
  path: /iplant/home/shared/iplantcollaborative/testing_tools/cowsay
  kind: file
  filetypes:
    - txt
```

Any values provided to `filetypes` will be joined (with `,`) and substituted for `$FILETYPES` in your workflow's command. Use this to inform your code which filetypes to expect, e.g.:

```yaml
commands: ls "$INPUT"/*.{"$FILETYPES"} >> things_cow_say.txt
input:
  path: /iplant/home/shared/iplantcollaborative/testing_tools/cowsay
  kind: file
  filetypes:
    - txt
    - md     
```

#### Workflow output

If your workflow produces outputs, add an `output` section with a `path` attribute to your configuration file. This attribute may be left blank if your workflow writes output files to the working directory; otherwise the value should be a directory path relative to the working directory. For example, to indicate that your workflow will deposit output files in a directory `output/directory` relative to the workflow's working directory:

```yaml
output:
  path: output/directory
```

By default, all files under the given `path` are uploaded to the location in the CyVerse Data Store provided by the user. To explicitly indicate which files to include/exclude (this is suggested especially if you workflow deposits files in the working directory), add `include` and `exclude` sections under `output`:

```yaml
output:
  path: output/directory
  include:
    patterns:                           # include excel files
      - xlsx                            # and png files
    names:                              
      - important.jpg                   # but only this .jpg file
  exclude:
    patterns:
      - temp                            # don't include anything marked temp
    names:
      - not_important.xlsx              # and exclude a particularexcel file
```

If only an `include` section is provided, only the file patterns and names specified will be included. If only an `exclude` section is present, all files except the patterns and names specified will be included. If you provide both `include` and `exclude` sections, the `include` rules will first be applied to generate a subset of files, which will then be filtered by the `exclude` rules.

#### A super simple example

The following workflow prints the content of an input file and then writes it to an output file (located in the same working directory):

```yaml
name: Hello File
author: 
image: docker://alpine
public: True
clone: False
commands: cat "$INPUT" && cat "$INPUT" >> cowsaid.txt
input:
  from: /iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt
  kind: file
output:
  path: # blank to indicate working directory
  include:
    names:                              
      - cowsaid.txt
```

PlantIT will prompt users of your workflow to select an input file from the CyVerse Data Store, providing the given shared file as a default.
