def status(job_identifier):
    print(f'GET /jobs/{job_identifier}/execution')


def start(job_identifier):
    print(f'POST /jobs/{job_identifier}/execution')


def change(job_identifier):
    print(f'PUT /jobs/{job_identifier}/execution')


def stop(job_identifier):
    print(f'DELETE /jobs/{job_identifier}/execution')
