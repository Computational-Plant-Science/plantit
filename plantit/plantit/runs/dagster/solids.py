import json

from dagster import solid


@solid(required_resource_keys={'ssh'})
def upload_pipeline(context, pipeline: dict, directory: str):
    with context.resources.ssh as ssh:
        with ssh.client.sftp as sftp:
            sftp.chdir(directory)
            with sftp.open('pipeline.json', 'w') as file:
                file.write(json.dumps(pipeline))


@solid(required_resource_keys={'ssh'})
def execute_command(context, command: str, directory: str):
    try:
        with context.resources.ssh as ssh:
            cmd = f"cd {directory}; {command}" if directory else command
            context.log .info(f"Executing command '{cmd}'")
            stdin, stdout, stderr = ssh.client.exec_command(cmd)
            stdin.close()
            for line in iter(lambda: stdout.readline(2048), ""):
                context.log.info(f"Received stdout from command '{command}': {line}")
            for line in iter(lambda: stderr.readline(2048), ""):
                context.log.warn(f"Received stderr from command '{command}': {line}")

            if stdout.channel.recv_exit_status():
                raise Exception(f"Received non-zero exit status from command '{command}'")
            else:
                context.log.info(
                    f"Successfully executed command '{command}'")
    except Exception:
        msg = f"Failed to execute command '{command}'"
        context.log.error(msg)