def get_all():
    """
    Return a specific pipeline.
    """
    print('GET /jobs')
    return {        
    }


def new(pipeline_id, interval):
    """
    Return a list of all known pipelines.
    """
    print(f'POST /jobs, pipeline_id:{pipeline_id}, interval:{interval}')
    return {}

def create():
    print('POST /jobs')

def get_one(job_identifier):
    """
    Use job-identifier to search in both id and name
    """
    return {}

def delete(job_identifier):
    return {}

def change(job_identifier):
    return {}    