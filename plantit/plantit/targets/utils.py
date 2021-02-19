def singularity_cache_clean_task_name(target: str):
    return f"Clean singularity cache on {target}"


def run_workdir_clean_task_name(target: str, run_id: str):
    return f"Clean working directory for run {run_id} on {target}"
