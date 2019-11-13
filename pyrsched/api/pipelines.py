def get_one(filename):
    """
    Return a specific pipeline.
    """
    print(f'GET /pipelines/{filename}')
    return {
        'filename': filename,
    }


def get_all():
    """
    Return a list of all known pipelines.
    """
    print('GET /pipelines')
    return [
        {}
    ]


def create(filename):
    print(f'POST /pipelines/{filename}')
    return {}


def update(filename):
    print(f'PUT /pipelines/{filename}')
    return {}


def delete(filename):
    print(f'DELETE /pipelines/{filename}')
    return {}
