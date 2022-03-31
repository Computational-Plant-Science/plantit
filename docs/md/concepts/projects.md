# <i class="fas fa-seedling fa-1x fa-fw"></i> **Projects**

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


<!-- END doctoc generated TOC please keep comment here to allow auto update -->

A <i class="fas fa-seedling fa-1x fa-fw"></i> **Project** is a [MIAPPE](https://github.com/MIAPPE/MIAPPE) investigation: a formal ontology for metadata describing a phenotyping experiment.

![Entity relational diagram](../../media/miappe.png)

The MIAPPE schema permits one or more studies to be associated with each investigation. Each study describes a particular instance of an experiment, with properties such as start/end dates, location, environmental parameters, etc.

Currently `plantit` allows users to associate projects and studies with tasks, linking computational analyses to their experimental context. Eventually we also intend to support:

- associating studies with one or more datasets
- tagging data objects as samples of biological materials
- image annotations
