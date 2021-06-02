from os.path import join

from plantit.submissions.models import Submission


def map_old_workflow_config_to_new(old: dict, run: Submission, resources: dict) -> dict:
    new_config = {
        'image': old['config']['image'],
        'command': old['config']['commands'],
        'workdir': old['config']['workdir'],
        'log_file': f"{run.guid}.{run.agent.name.lower()}.log"
    }

    del old['config']['agent']

    if 'mount' in old['config']:
        new_config['bind_mounts'] = old['config']['mount']

    if 'parameters' in old['config']:
        old_params = old['config']['parameters']
        params = []
        for p in old_params:
            if p['type'] == 'string':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'select':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'number':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'boolean':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
        new_config['parameters'] = params

    if 'input' in old['config']:
        input_kind = old['config']['input']['kind'] if 'kind' in old['config']['input'] else None
        new_config['input'] = dict()
        if input_kind == 'directory':
            new_config['input']['directory'] = dict()
            new_config['input']['directory']['path'] = join(run.agent.workdir, run.workdir, 'input')
            new_config['input']['directory']['patterns'] = old['config']['input']['patterns']
        elif input_kind == 'files':
            new_config['input']['files'] = dict()
            new_config['input']['files']['path'] = join(run.agent.workdir, run.workdir, 'input')
            new_config['input']['files']['patterns'] = old['config']['input']['patterns']
        elif input_kind == 'file':
            new_config['input']['file'] = dict()
            new_config['input']['file']['path'] = join(run.agent.workdir, run.workdir, 'input',
                                                       old['config']['input']['from'].rpartition('/')[2])

    sandbox = run.agent.name == 'Sandbox'
    work_dir = join(run.agent.workdir, run.workdir)
    if not sandbox and not run.agent.job_array:
        new_config['jobqueue'] = dict()
        new_config['jobqueue']['slurm'] = {
            'cores': resources['cores'],
            'processes': resources['processes'],
            'walltime': resources['time'],
            'local_directory': work_dir,
            'log_directory': work_dir,
            'env_extra': [run.agent.pre_commands]
        }

        if 'mem' in resources:
            new_config['jobqueue']['slurm']['memory'] = resources['mem']
        if run.agent.queue is not None and run.agent.queue != '':
            new_config['jobqueue']['slurm']['queue'] = run.agent.queue
        if run.agent.project is not None and run.agent.project != '':
            new_config['jobqueue']['slurm']['project'] = run.agent.project
        if run.agent.header_skip is not None and run.agent.header_skip != '':
            new_config['jobqueue']['slurm']['header_skip'] = run.agent.header_skip.split(',')

        if 'gpu' in old['config'] and old['config']['gpu']:
            if run.agent.gpu:
                print(f"Using GPU on {run.agent.name} queue '{run.agent.gpu_queue}'")
                new_config['gpu'] = True
                new_config['jobqueue']['slurm']['job_extra'] = [f"--gres=gpu:1"]
                new_config['jobqueue']['slurm']['queue'] = run.agent.gpu_queue
            else:
                print(f"No GPU support on {run.agent.name}")

    return new_config
