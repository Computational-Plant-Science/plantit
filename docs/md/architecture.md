# Architecture

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Overview](#overview)
- [Dependencies](#dependencies)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview

PlantIT is middleware binding GitHub and CyVerse to various institutional clusters & supercomputers via a web interface.

![PlantIT Architecture Diagram](../media/plantit.jpg)

## Dependencies

A Python package, `plantit-cli`, must be installed on deployment targets prior to application integration, however this is an adminstrator task. No further installation is required. End-users simply link their CyVerse and GitHub accounts, then enter their own credentials for or request access to public computer systems.