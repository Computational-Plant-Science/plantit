import re
import traceback
from os.path import join

import yaml

from plantit.celery import app
from plantit.runs.models import Run, Status
from plantit.runs.ssh import SSH


def clean_html(raw_html):
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text


def execute_command(run: Run, ssh_client: SSH, pre_command: str, command: str, directory: str):
    cmd = f"{pre_command} && cd {directory} && {command}" if directory else command
    print(f"Executing remote command: '{cmd}'")
    stdin, stdout, stderr = ssh_client.client.exec_command(cmd)
    stdin.close()
    for line in iter(lambda: stdout.readline(2048), ""):
        print(f"Received stdout from remote command: '{clean_html(line)}'")
    for line in iter(lambda: stderr.readline(2048), ""):
        print(f"Received stderr from remote command: '{clean_html(line)}'")

    if stdout.channel.recv_exit_status():
        raise Exception(f"Received non-zero exit status from remote command")
    else:
        print(f"Successfully executed remote command.")


@app.task()
def execute(workflow, run_id, plantit_token, cyverse_token):
    run = Run.objects.get(identifier=run_id)

    try:
        work_dir = join(run.target.workdir, run.work_dir)
        ssh_client = SSH(run.target.hostname,
                         run.target.port,
                         run.target.username)

        with ssh_client:
            execute_command(run=run, ssh_client=ssh_client, pre_command=':', command=f"mkdir {work_dir}",
                            directory=run.target.workdir)
            msg = f"Created working directory '{work_dir}'. Uploading flow definition..."
            print(msg)
            run.status_set.create(description=msg, state=Status.RUNNING, location='PlantIT')
            run.save()

            with ssh_client.client.open_sftp() as sftp:
                sftp.chdir(work_dir)
                with sftp.open('workflow.yaml', 'w') as workflow_def:
                    yaml.dump(workflow['config'], workflow_def, default_flow_style=False)

                if run.target.executor == 'slurm':
                    msg = "Uploading job script..."
                    print(msg)
                    run.status_set.create(description=msg, state=Status.RUNNING, location='PlantIT')
                    run.save()
                    with sftp.open('../job.sh', 'r') as template_script, sftp.open('job.sh', 'w') as script:
                        for line in template_script:
                            if 'SBATCH --partition' in line and 'queue' in workflow['config']['executor']['jobqueue']['slurm']:
                                line = line.split('=')[0] + '=' + workflow['config']['executor']['jobqueue']['slurm']['queue'] + '\n'
                            if 'SBATCH --ntasks' in line and 'processes' in workflow['config']['executor']['jobqueue']['slurm']:
                                line = line.split('=')[0] + '=' + str(workflow['config']['executor']['jobqueue']['slurm']['processes']) + '\n'
                            if 'SBATCH --time' in line and 'walltime' in workflow['config']['executor']['jobqueue']['slurm']:
                                line = line.split('=')[0] + '=' + workflow['config']['executor']['jobqueue']['slurm']['walltime'] + '\n'
                            if 'SBATCH -A' in line and 'project' in workflow['config']['executor']['jobqueue']['slurm']:
                                line = line.split('=')[0] + '=' + workflow['config']['executor']['jobqueue']['slurm']['project']+ '\n'
                            script.write(line)
                        script.write(f"plantit workflow.yaml --plantit_token '{plantit_token}' --cyverse_token '{cyverse_token}'")

            msg = "Running flow..."
            print(msg)
            run.status_set.create(description=msg, state=Status.RUNNING, location='PlantIT')
            run.save()

            pre_commands = '; '.join(
                str(run.target.pre_commands).splitlines()) if run.target.pre_commands else ':'
            print(f"Pre-commands: {pre_commands}")

            execute_command(run=run,
                            ssh_client=ssh_client,
                            pre_command=pre_commands,
                            command=f"{'plantit workflow.yaml --plantit_token ' + plantit_token + ' --cyverse_token ' + cyverse_token if 'local' in workflow['config']['executor'] else 'chmod +x job.sh && sbatch job.sh'}",
                            directory=work_dir)

            print(f"Run completed.")
            if run.status.state != 2:
                run.status_set.create(
                    description=f"Run completed.",
                    state=Status.COMPLETED,
                    location='PlantIT')
            else:
                run.status_set.create(
                    description=f"Run failed.",
                    state=Status.FAILED,
                    location='PlantIT')

            run.save()

    except Exception:
        run.status_set.create(
            description=f"Run failed: {traceback.format_exc()}.",
            state=Status.FAILED,
            location='PlantIT')
        run.save()