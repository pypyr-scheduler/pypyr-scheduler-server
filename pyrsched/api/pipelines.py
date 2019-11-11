def get(pipeline_id):
    print(f'GET /pipelines/{pipeline_id}')
    return {
        'id': pipeline_id,
    }


def all():
    print('GET /pipelines')
    return [
        {}
    ]
