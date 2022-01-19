from typing import List

from plantit import docker as docker, terrain as terrain


def validate_workflow_configuration(config: dict, terrain_token: str = None) -> (bool, List[str]):
    """
    Verifies that the given configuration is valid.
    Note that this function is IO-bound and makes up to 2 network calls:
        - checking Docker image availability on Docker Hub
        - making sure Terrain collection or object exists

    Args:
        config: The task configuration
        terrain_token: The token to authenticate with Terrain

    Returns:

    """
    errors = []

    # name (required)
    if 'name' not in config: errors.append('Missing attribute \'name\'')
    elif type(config['name']) is not str:
        errors.append('Attribute \'name\' must be a str')

    # author (required)
    if 'author' not in config:
        errors.append('Missing attribute \'author\'')
    else:
        author = config['author']
        if (type(config['author']) is str and config['author'] == '') or (type(author) is list and not all(type(d) is str for d in author)):
            errors.append('Attribute \'author\' must be a non-empty str or list of str')

    # image (required)
    if 'image' not in config:
        errors.append('Missing attribute \'image\'')
    elif type(config['image']) is not str:
        errors.append('Attribute \'image\' must be a str')
    else:
        image_owner, image_name, image_tag = docker.parse_image_components(config['image'])
        if 'docker' in config['image'] and not docker.image_exists(image_name, image_owner, image_tag):
            errors.append(f"Image '{config['image']}' not found on Docker Hub")

    # commands (required)
    if 'commands' not in config:
        errors.append('Missing attribute \'commands\'')
    elif type(config['commands']) is not str:
        errors.append('Attribute \'commands\' must be a str')

    # environment variables
    if 'env' in config:
        if type(config['env']) is not list:
            errors.append('Attribute \'env\' must be a list')
        elif config['env'] is None or len(config['env']) == 0:
            errors.append('Attribute \'env\' must not be empty')

    # mount
    if 'mount' in config:
        if type(config['mount']) is not list:
            errors.append('Attribute \'mount\' must be a list')
        elif config['mount'] is None or len(config['mount']) == 0:
            errors.append('Attribute \'mount\' must not be empty')

    # gpu
    if 'gpu' in config:
        if type(config['gpu']) is not bool:
            errors.append('Attribute \'mount\' must be a bool')

    # tags
    if 'tags' in config:
        if type(config['tags']) is not list:
            errors.append('Attribute \'tags\' must be a list')

    # legacy input format
    if 'from' in config:
        errors.append('Attribute \'from\' is deprecated; use an \'input\' section instead')

    # input
    if 'input' in config:
        # path
        if 'path' not in config['input']:
            errors.append('Missing attribute \'input.path\'')
        if config['input']['path'] != '' and config['input']['path'] is not None:
            if terrain_token is None: raise ValueError(f"Terrain token not provided!")
            cyverse_path_result = terrain.path_exists(config['input']['path'], terrain_token)
            if type(cyverse_path_result) is bool and not cyverse_path_result:
                errors.append('Attribute \'input.path\' must be a str (either empty or a valid path in the CyVerse Data Store)')

        # kind
        if 'kind' not in config['input']:
            errors.append('Missing attribute \'input.kind\'')
        if not (config['input']['kind'] == 'file' or config['input']['kind'] == 'files' or config['input']['kind'] == 'directory'):
            errors.append('Attribute \'input.kind\' must be a string (either \'file\', \'files\', or \'directory\')')

        # legacy filetypes format
        if 'patterns' in config['input']:
            errors.append('Attribute \'input.patterns\' is deprecated; use \'input.filetypes\' instead')

        # filetypes
        if 'filetypes' in config['input']:
            if type(config['input']['filetypes']) is not list or not all(type(pattern) is str for pattern in config['input']['filetypes']):
                errors.append('Attribute \'input.filetypes\' must be a list of str')

    # legacy output format
    if 'to' in config:
        errors.append('Attribute \'to\' is deprecated; use an \'output\' section instead')

    # output
    if 'output' in config:
        # path
        if 'path' not in config['output']:
            errors.append('Attribute \'output\' must include attribute \'path\'')
        if config['output']['path'] is not None and type(config['output']['path']) is not str:
            errors.append('Attribute \'output.path\' must be a str')

        # include
        if 'include' in config['output']:
            if 'patterns' in config['output']['include']:
                if type(config['output']['include']['patterns']) is not list or not all(
                        type(pattern) is str for pattern in config['output']['include']['patterns']):
                    errors.append('Attribute \'output.include.patterns\' must be a list of str')
            if 'names' in config['output']['include']:
                if type(config['output']['include']['names']) is not list or not all(
                        type(name) is str for name in config['output']['include']['names']):
                    errors.append('Attribute \'output.include.names\' must be a list of str')

        # exclude
        if 'exclude' in config['output']:
            if 'patterns' in config['output']['exclude']:
                if type(config['output']['exclude']['patterns']) is not list or not all(
                        type(pattern) is str for pattern in config['output']['exclude']['patterns']):
                    errors.append('Attribute \'output.exclude.patterns\' must be a list of str')
            if 'names' in config['output']['exclude']:
                if type(config['output']['exclude']['names']) is not list or not all(
                        type(name) is str for name in config['output']['exclude']['names']):
                    errors.append('Attribute \'output.exclude.names\' must be a list of str')

    # doi (optional)
    if 'doi' in config:
        doi = config['doi']
        if (type(doi) is str and doi == '') or (type(doi) is list and not all(type(d) is str for d in doi)):
            errors.append('Attribute \'doi\' must be a non-empty str or list of str')

    # walltime (optional)
    if 'walltime' in config:
        walltime = config['walltime']
        import re
        pattern = re.compile("^([0-9][0-9]:[0-9][0-9]:[0-9][0-9])$")
        if type(walltime) is not str:
            errors.append('Attribute \'walltime\' must be a str')
        if type(walltime) is str and not bool(pattern.match(walltime)):
            errors.append('Attribute \'walltime\' must have format XX:XX:XX')


    return (True, []) if len(errors) == 0 else (False, errors)