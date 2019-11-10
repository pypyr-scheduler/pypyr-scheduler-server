def get():
    print('GET /status')
    return {
        'is_running': True,
    }
