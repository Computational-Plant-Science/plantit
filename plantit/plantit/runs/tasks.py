import binascii
import os
import traceback
from datetime import timedelta
from os import environ
from os.path import join

import yaml
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from django.utils import timezone

from plantit import settings
from plantit.celery import app
from plantit.runs.models import Run
from plantit.runs.ssh import SSH
from plantit.runs.utils import update_log, execute_command, old_flow_config_to_new, parse_walltime
from plantit.targets.models import Target

logger = get_task_logger(__name__)


def __create_run(username, flow, target, task_id) -> Run:
    walltime = parse_walltime(flow['config']['target']['resources']['time']) if 'resources' in flow['config']['target'] else timedelta(minutes=10)
    now = timezone.now()
    run = Run.objects.create(
        user=User.objects.get(username=username),
        flow_owner=flow['repo']['owner']['login'],
        flow_name=flow['repo']['name'],
        target=target,
        created=now,
        task_id=task_id,
        work_dir=task_id + "/",
        remote_results_path=task_id + "/",
        token=binascii.hexlify(os.urandom(20)).decode(),
        walltime=walltime.total_seconds(),
        timeout=walltime.total_seconds() * int(settings.RUNS_TIMEOUT_MULTIPLIER))  # multiplier allows for cluster scheduler delay

    # add tags
    for tag in flow['config']['tags']:
        run.tags.add(tag)

    run.save()
    return run


def __upload(flow, run, target, ssh):
    # update flow config before uploading
    flow['config']['task_id'] = run.task_id
    flow['config']['workdir'] = join(target.workdir, run.task_id)
    flow['config']['log_file'] = f"{run.task_id}.{target.name.lower()}.log"
    if 'output' in flow['config']:
        flow['config']['output']['from'] = join(target.workdir, run.work_dir, flow['config']['output']['from'])

    # if flow has outputs, make sure we don't push configuration or job scripts
    if 'output' in flow['config']:
        flow['config']['output']['exclude']['names'] = [
            "flow.yaml",
            "template_local_run.sh",
            "template_slurm_run.sh"]

    resources = None if 'resources' not in flow['config']['target'] else flow['config']['target']['resources']  # cluster resource requests, if any
    callback_url = settings.API_URL + 'runs/' + run.task_id + '/status/'  # PlantIT status update callback URL
    work_dir = join(run.target.workdir, run.work_dir)
    new_flow = old_flow_config_to_new(flow, run, resources)  # TODO update flow UI page

    # create working directory
    execute_command(ssh_client=ssh, pre_command=':', command=f"mkdir {work_dir}", directory=run.target.workdir)

    # upload flow config and job script
    with ssh.client.open_sftp() as sftp:
        sftp.chdir(work_dir)

        # TODO refactor to allow multiple cluster schedulers
        sandbox = run.target.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
        template = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
        template_name = template.split('/')[-1]

        # upload flow config file
        with sftp.open('flow.yaml', 'w') as flow_file:
            yaml.dump(new_flow, flow_file, default_flow_style=False)

        # compose and upload job script
        with open(template, 'r') as template_script, sftp.open(template_name, 'w') as script:
            for line in template_script:
                script.write(line)

            if not sandbox:  # we're on a SLURM cluster, so add resource requests
                script.write("#SBATCH -N 1\n")
                if 'tasks' in resources:
                    script.write(f"#SBATCH --ntasks={resources['tasks']}\n")
                if 'cores' in resources:
                    script.write(f"#SBATCH --cpus-per-task={resources['cores']}\n")
                if 'time' in resources:
                    script.write(f"#SBATCH --time={resources['time']}\n")
                if 'mem' in resources and (run.target.header_skip is None or '--mem' not in str(run.target.header_skip)):
                    script.write(f"#SBATCH --mem={resources['mem']}\n")
                if run.target.queue is not None and run.target.queue != '':
                    script.write(f"#SBATCH --partition={run.target.gpu_queue if run.target.gpu else run.target.queue}\n")
                if run.target.project is not None and run.target.project != '':
                    script.write(f"#SBATCH -A {run.target.project}\n")
                script.write("#SBATCH --mail-type=END,FAIL\n")
                script.write(f"#SBATCH --mail-user={run.user.email}\n")
                script.write("#SBATCH --output=PlantIT.%j.out\n")
                script.write("#SBATCH --error=PlantIT.%j.err\n")

            # add precommands
            script.write(run.target.pre_commands + '\n')

            # if we have inputs, add pull command
            if 'input' in flow['config']:
                sftp.mkdir(join(run.target.workdir, run.work_dir, 'input'))
                pull_commands = f"plantit terrain pull {flow['config']['input']['from']}" \
                                f" -p {join(run.target.workdir, run.work_dir, 'input')}" \
                                f" {' '.join(['--pattern ' + pattern for pattern in flow['config']['input']['patterns']])}" \
                                f""f" --plantit_url '{callback_url}'" \
                                f""f" --plantit_token '{run.token}'" \
                                f""f" --terrain_token {run.user.profile.cyverse_token}\n"
                logger.info(f"Using pull command: {pull_commands}")
                script.write(pull_commands)

            # add run command
            run_commands = f"plantit run flow.yaml --plantit_url '{callback_url}' --plantit_token '{run.token}'"
            docker_username = environ.get('DOCKER_USERNAME', None)
            docker_password = environ.get('DOCKER_PASSWORD', None)
            if docker_username is not None and docker_password is not None:
                run_commands += f" --docker_username {docker_username} --docker_password {docker_password}"
            run_commands += "\n"
            logger.info(f"Using run command: {run_commands}")
            script.write(run_commands)

            # if we have outputs...
            if 'output' in flow:
                # add zip command...
                zip_commands = f"plantit zip {flow['output']['from']}"
                if 'include' in flow['output']:
                    if 'patterns' in flow['output']['include']:
                        zip_commands = zip_commands + ' '.join(['--include_pattern ' + pattern for pattern in flow['output']['include']['patterns']])
                    if 'names' in flow['output']['include']:
                        zip_commands = zip_commands + ' '.join(['--include_name ' + pattern for pattern in flow['output']['include']['names']])
                    if 'patterns' in flow['output']['exclude']:
                        zip_commands = zip_commands + ' '.join(['--exclude_pattern ' + pattern for pattern in flow['output']['exclude']['patterns']])
                    if 'names' in flow['output']['exclude']:
                        zip_commands = zip_commands + ' '.join(['--exclude_name ' + pattern for pattern in flow['output']['exclude']['names']])
                zip_commands += '\n'
                logger.info(f"Using zip command: {zip_commands}")

                # and add push command if we have a destination
                if 'to' in flow['output']:
                    push_commands = f"plantit terrain push {flow['output']['to']}" \
                                    f" -p {join(run.workdir, flow['output']['from'])}" \
                                    f" --plantit_url '{callback_url}'" \
                                    f" --plantit_token '{run.token}'" \
                                    f" --terrain_token {run.user.profile.cyverse_token}"
                    if 'include' in flow['output']:
                        if 'patterns' in flow['output']['include']:
                            push_commands = push_commands + ' '.join(['--include_pattern ' + pattern for pattern in flow['output']['include']['patterns']])
                        if 'names' in flow['output']['include']:
                            push_commands = push_commands + ' '.join(['--include_name ' + pattern for pattern in flow['output']['include']['names']])
                        if 'patterns' in flow['output']['exclude']:
                            push_commands = push_commands + ' '.join(['--exclude_pattern ' + pattern for pattern in flow['output']['exclude']['patterns']])
                        if 'names' in flow['output']['exclude']:
                            push_commands = push_commands + ' '.join(['--exclude_name ' + pattern for pattern in flow['output']['exclude']['names']])
                    push_commands += '\n'
                    script.write(push_commands)
                    logger.info(f"Using push command: {push_commands}")


def __submit(run, ssh):
    # TODO refactor to allow multiple cluster schedulers
    sandbox = run.target.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
    template = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
    template_name = template.split('/')[-1]
    work_dir = join(run.target.workdir, run.work_dir)
    pre_command = '; '.join(str(run.target.pre_commands).splitlines()) if run.target.pre_commands else ':'
    command = f"chmod +x {template_name} && ./{template_name}" if sandbox else f"chmod +x {template_name} && sbatch {template_name}"

    execute_command(ssh_client=ssh, pre_command=pre_command, command=command, directory=work_dir)


@app.task(bind=True, track_started=True)
def execute(self, username, flow):
    try:
        target = Target.objects.get(name=flow['config']['target']['name'])
        run = __create_run(username, flow, target, execute.request.id)

        description = f"Deploying run {execute.request.id} to {target.name}"
        logger.info(description)
        update_log(execute.request.id, description)

        # TODO orchestrate these steps independently within this task, rather than stringing them together in 1 script?
        ssh = SSH(run.target.hostname, run.target.port, run.target.username)
        with ssh:
            # upload run config file and script
            description = f"Creating working directory and uploading files"
            logger.info(description)
            self.update_state(state='UPLOADING', meta={'description': description})
            update_log(execute.request.id, description)
            __upload(flow, run, target, ssh)

            # schedule a checkup task to run after walltime elapses
            checkup.s(execute.request.id).apply_async(countdown=run.walltime)

            # submit run
            description = 'Running script' if run.target.name == 'Sandbox' else 'Submitting script to scheduler'
            logger.info(description)
            self.update_state(state='RUNNING', meta={'description': description})
            update_log(execute.request.id, description)
            __submit(run, ssh)

            # schedule a cleanup task to run after timeout elapses
            cleanup.s(execute.request.id).apply_async(countdown=run.timeout)
    except Exception:
        description = f"Run {execute.request.id} failed: {traceback.format_exc()}."
        logger.error(description)
        update_log(execute.request.id, description)
        raise


@app.task()
def checkup(task_id):
    task = AsyncResult(task_id, app=app)
    run = Run.objects.get(task_id=task_id)

    logger.info(f"Checking status of run {task_id}")

    # TODO:
    # - if the run failed (check the cluster scheduler), delete everything in the run working directory but the log files

    # otherwise schedule a cleanup task to run after timeout elapses
    cleanup.s(execute.request.id).apply_async(countdown=run.timeout)  # TODO adjustable period (1 day? 1 week?)



@app.task()
def cleanup(task_id):
    task = AsyncResult(task_id, app=app)
    run = Run.objects.get(task_id=task_id)

    logger.info(f"Cleaning up run {task_id}")

    # TODO:
    # - if the run failed, delete everything in the run working directory but the log files
    # - if the run completed,

    # try:
    #     # if task is completed or failed, cancel its task
    #     if run.status != 0 and run.status != 6:
    #         app.control.terminate(task_id)
    #         logger.info(f"Timed out after {timedelta(seconds=run.timeout)}")
    #         update_status(run, Status.FAILED, f"Timed out after {timedelta(seconds=run.timeout)}")
    # except:
    #     logger.error(f"Cleanup failed: {traceback.format_exc()}")
    #     update_status(run, Status.FAILED, f"Cleanup failed: {traceback.format_exc()}")
