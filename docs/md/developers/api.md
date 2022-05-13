# Web API

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Endpoints](#endpoints)
  - [Stats](#stats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

`plantit` exposes an API for programmatic queries about usage statistics and public resources. Endpoints are exposed at the root URL `https://plantit.cyverse.org/apis/v1/`, documented with Swagger at [`https://plantit.cyverse.org/apis/v1/swagger/`](https://plantit.cyverse.org/apis/v1/swagger/).

## Endpoints

Currently only public usage statistics are reported by the `plantit` API. Support for BrAPI is under consideration and may be developed in the future. We may also support token-authenticated task orchestration at some point.

### Stats

The `/stats/` routes return usage data for `plantit` users, publicly available workflows and execution targets. Four endpoints are available:

- `/stats/counts`: cumulative user and resource counts
- `/stats/institutions`: user-represented institutions
- `/stats/timeseries`: usage timeseries for public workflows and execution targets
- `/stats/timeseries/<owner>/<name>/<branch>`: usage timeseries for a particular public workflow

