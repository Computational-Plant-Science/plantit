from os.path import join

from plantit.runs.models import Run
from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command


def get_job_walltime(run: Run) -> (str, str):
    ssh = SSH(run.target.hostname, run.target.port, run.target.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=":",
            command=f"squeue --user={run.target.username}",
            directory=join(run.target.workdir, run.work_dir),
            allow_stderr=True)

        try:
            job_line = next(l for l in lines if run.job_id in l)
            job_split = job_line.split()
            job_walltime = job_split[-3]
            return job_walltime
        except StopIteration:
            return None


def get_job_status(run: Run) -> str:
    ssh = SSH(run.target.hostname, run.target.port, run.target.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"sacct -j {run.job_id}",
            directory=join(run.target.workdir, run.work_dir),
            allow_stderr=True)

        job_line = next(l for l in lines if run.job_id in l)
        job_split = job_line.split()
        job_status = job_split[5].replace('+', '')
        return job_status
    pass


def cancel_job(run: Run):
    ssh = SSH(run.target.hostname, run.target.port, run.target.username)
    with ssh:
        execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"scancel {run.job_id}",
            directory=join(run.target.workdir, run.work_dir))
