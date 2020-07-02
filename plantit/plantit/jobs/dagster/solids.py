from dagster import solid


@solid(required_resource_keys={'ssh'})
def transfer_github_repository(context, repository_url: str, working_directory: str):
    try:
        with context.resources.ssh as ssh:
            pass
    except Exception:
        msg = f"Failed to transfer Github repository '{repository_url}' to '{working_directory}'"
        context.log.error(msg)


@solid(required_resource_keys={'ssh'})
def execute_command(context, command: str, working_directory: str = None):
    try:
        with context.resources.ssh as ssh:
            cmd = f"cd {working_directory}; {command}" if working_directory else command
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