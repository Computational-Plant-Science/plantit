import os
import re
import traceback
from os.path import join

from datetime import datetime, timedelta

import yaml
from celery.schedules import crontab

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
def execute(flow, run_id, plantit_token, cyverse_token):
    run = Run.objects.get(identifier=run_id)

    try:
        work_dir = join(run.target.workdir, run.work_dir)
        ssh_client = SSH(run.target.hostname,
                         run.target.port,
                         run.target.username)

        with ssh_client:
            execute_command(run=run,
                            ssh_client=ssh_client,
                            pre_command=':',
                            command=f"mkdir {work_dir}",
                            directory=run.target.workdir)

            msg = f"Created working directory '{work_dir}'. Uploading flow definition..."
            print(msg)
            run.status_set.create(description=msg, state=Status.RUNNING, location='PlantIT')
            run.save()

            with ssh_client.client.open_sftp() as sftp:
                sftp.chdir(work_dir)
                with sftp.open('flow.yaml', 'w') as flow_def:
                    if ['resources'] not in flow['config']['target']:
                        resources = None
                    else:
                        resources = flow['config']['target']['resources']
                    del flow['config']['target']
                    yaml.dump(flow['config'], flow_def, default_flow_style=False)

                    msg = "Uploading script..."
                    print(msg)
                    run.status_set.create(description=msg, state=Status.RUNNING, location='PlantIT')
                    run.save()

                    sandbox = run.target.name == 'Sandbox'
                    template = os.environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else os.environ.get(
                        'CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
                    print(f"Template: {template}")
                    template_name = template.split('/')[-1]
                    with open(template, 'r') as template_script, sftp.open(template_name, 'w') as script:
                        for line in template_script:
                            script.write(line)
                        if not sandbox:
                            if 'SBATCH --partition' in line and 'queue' in resources:
                                script.write(line.split('=')[0] + '=' + resources['queue'] + '\n')
                            elif 'SBATCH -A' in line and 'project' in resources:
                                script.write(line.split('=')[0] + '=' + resources['project'] + '\n')
                            elif 'SBATCH --ntasks' in line and 'processes' in resources:
                                script.write(line.split('=')[0] + '=' + str(resources['processes']) + '\n')
                            elif 'SBATCH --cpus-per-task' in line and 'cores' in resources:
                                script.write(line.split('=')[0] + '=' + str(resources['cores']) + '\n')
                            elif 'SBATCH --time' in line and 'walltime' in resources:
                                script.write(line.split('=')[0] + '=' + resources['walltime'] + '\n')
                            script.write("#SBATCH --mail-type=END,FAIL\n")
                            script.write(f"#SBATCH --mail-user={run.user.email}\n")
                            script.write("#SBATCH --output=PlantIT.%j.out\n")
                            script.write("#SBATCH --error=PlantIT.%j.err\n")
                        script.write(run.target.pre_commands + '\n')
                        script.write(
                            f"plantit flow.yaml --plantit_token '{plantit_token}' --cyverse_token '{cyverse_token}'\n")

            execute_command(run=run,
                            ssh_client=ssh_client,
                            pre_command='; '.join(
                                str(run.target.pre_commands).splitlines()) if run.target.pre_commands else ':',
                            command=f"chmod +x {template_name} && ./{template_name}" if sandbox else f"chmod +x {template_name} && sbatch {template_name}",
                            directory=work_dir)

            if run.status.state != 2:
                msg = f"Run '{run.identifier}' {'completed' if sandbox else 'submitted'}."
                run.status_set.create(
                    description=msg,
                    state=Status.COMPLETED if sandbox else Status.RUNNING,
                    location='PlantIT')
            else:
                msg = f"Run '{run.identifier}' failed."
                print(msg)
                run.status_set.create(
                    description=msg,
                    state=Status.FAILED,
                    location='PlantIT')

            run.save()

    except Exception:
        msg = f"Run failed: {traceback.format_exc()}."
        run.status_set.create(
            description=msg,
            state=Status.FAILED,
            location='PlantIT')
        run.save()


@app.task()
def remove_old_runs():
    epoch = datetime.fromordinal(0)
    threshold = datetime.now() - timedelta(days=30)
    epoch_ts = f"{epoch.year}-{epoch.month}-{epoch.day}"
    threshold_ts = f"{threshold.year}-{threshold.month}-{threshold.day}"
    print(f"Removing runs created before {threshold.strftime('%d/%m/%Y %H:%M:%S')}")
    Run.objects.filter(date__range=[epoch_ts, threshold_ts]).delete()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30),
        remove_old_runs.s())
