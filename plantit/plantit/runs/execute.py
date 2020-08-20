import re
import traceback
from os.path import join

import yaml

from plantit.celery import app
from plantit.runs.run import Run
from plantit.runs.ssh import SSH
from plantit.runs.status import Status


def clean_html(raw_html):
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text


def execute_command(run: Run, ssh_client: SSH, pre_command: str, command: str, directory: str):
    cmd = f"cd {directory}; {pre_command}; {command}" if directory else command
    print(f"Executing remote command: '{cmd}'")
    stdin, stdout, stderr = ssh_client.client.exec_command(cmd)
    stdin.close()
    for line in iter(lambda: stdout.readline(2048), ""):
        print(f"Received stout from remote command: '{clean_html(line)}'")
    for line in iter(lambda: stderr.readline(2048), ""):
        print(f"Received sterr from remote command: '{clean_html(line)}'")

    if stdout.channel.recv_exit_status():
        raise Exception(f"Received non-zero exit status from remote command")
    else:
        print(f"Successfully executed remote command.")


@app.task()
def execute(workflow, run_id, token):
    run = Run.objects.get(identifier=run_id)
    run.status_set.create(description=f"Run started.",
                          state=Status.RUNNING,
                          location='PlantIT')
    run.save()

    try:
        work_dir = join(run.cluster.workdir, run.work_dir)
        ssh_client = SSH(run.cluster.hostname,
                         run.cluster.port,
                         run.cluster.username,
                         run.cluster.password) if run.cluster.password else SSH(run.cluster.hostname,
                                                                                run.cluster.port,
                                                                                run.cluster.username)

        with ssh_client:
            execute_command(run=run, ssh_client=ssh_client, pre_command=':', command=f"mkdir {work_dir}",
                            directory=run.cluster.workdir)
            print(f"Created working directory '{work_dir}'. Uploading workflow definition...")
            run.status_set.create(
                description=f"Created working directory. Uploading workflow definition...",
                state=Status.RUNNING,
                location='PlantIT')
            run.save()

            with ssh_client.client.open_sftp() as sftp:
                sftp.chdir(work_dir)
                with sftp.open('workflow.yaml', 'w') as file:
                    yaml.dump(workflow['config'], file, default_flow_style=False)
            print(f"Uploaded workflow definition to '{work_dir}'. Running workflow...")
            run.status_set.create(
                description=f"Uploaded workflow definition. Running workflow...",
                state=Status.RUNNING,
                location='PlantIT')
            run.save()

            execute_command(run=run, ssh_client=ssh_client, pre_command='; '.join(
                str(run.cluster.pre_commands).splitlines()) if run.cluster.pre_commands else ':',
                            command=f"plantit workflow.yaml --token {token}",
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