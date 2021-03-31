from os.path import join

from plantit.runs.models import Run
from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command


def get_job_walltime(run: Run) -> (str, str):
    ssh = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=":",
            command=f"squeue --user={run.cluster.username}",
            directory=join(run.cluster.workdir, run.work_dir),
            allow_stderr=True)

        try:
            job_line = next(l for l in lines if run.job_id in l)
            job_split = job_line.split()
            job_walltime = job_split[-3]
            return job_walltime
        except StopIteration:
            return None


def get_job_status(run: Run) -> str:
    ssh = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"sacct -j {run.job_id}",
            directory=join(run.cluster.workdir, run.work_dir),
            allow_stderr=True)

        job_line = next(l for l in lines if run.job_id in l)
        job_split = job_line.split()
        job_status = job_split[5].replace('+', '')
        return job_status
    pass


def cancel_run(run: Run):
    ssh = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)
    with ssh:
        if run.job_id is None or not any([run.job_id in r for r in execute_command(
                ssh_client=ssh,
                pre_command=':',
                command=f"squeue -u {run.cluster.username}",
                directory=join(run.cluster.workdir, run.work_dir))]):
            # run doesn't exist, so no need to cancel
            return

        execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"scancel {run.job_id}",
            directory=join(run.cluster.workdir, run.work_dir))

