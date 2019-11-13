def status(job_identifier):
    print (f'GET /jobs/{job-identifier}/execution')

def start(job_identifier):
    print (f'POST /jobs/{job-identifier}/execution')

def change(job_identifier):
    print (f'PUT /jobs/{job-identifier}/execution')

def stop(job_identifier):
    print (f'DELETE /jobs/{job-identifier}/execution')        