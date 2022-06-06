# Architecture

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Motivation](#motivation)
- [Technologies](#technologies)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Motivation

`plantit` is middleware binding GitHub and CyVerse to various institutional clusters & supercomputers via a web interface. Broadly, `plantit` aims to reinvent as little as possible, gluing existing tools together in ways that make data-intensive plant phenomics accessible and reproducible.

## Technologies

The `plantit` stack is predominantly Python. The backend is Nginx, Gunicorn, Django + Channels, Celery, Redis, & Postgres, orchestrated with Docker Compose. The frontend is Vue.

![Architecture](../../media/arch.jpg)

Feel free to [reach out](mailto:wbonelli@uga.edu) if you'd like to contribute to `plantit` development, start your own instance of `plantit` somewhere, modify it for another discipline, etc.
