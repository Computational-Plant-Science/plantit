# Architecture

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Architecture](#architecture)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

`plantit` is middleware binding GitHub and CyVerse to various institutional clusters & supercomputers via a web interface. The `plantit` stack is predominantly Python, including Django, Gunicorn, Celery, Postgres, Redis, & NGINX, defined with Docker Compose.

![Architecture](../media/plantit.jpg)
