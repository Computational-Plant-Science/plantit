class AbstractStatus:

    COMPLETED = 1
    FAILED = 2
    OK = 3
    WARN = 4
    CREATED = 5

    State = (
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (OK, 'OK'),
        (WARN, 'Warning'),
        (CREATED, 'Created')
    )

    job = None
    state = None
    date = None
    description = None
