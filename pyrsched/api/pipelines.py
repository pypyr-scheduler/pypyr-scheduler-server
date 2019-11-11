def get(pipeline_id):
    """
    Return a specific pipeline.
    """
    print(f'GET /pipelines/{pipeline_id}')
    return {
        'id': pipeline_id,
    }


def all():
    """
    Return a list of all known pipelines.
    """
    print('GET /pipelines')
    return [
        {}
    ]
