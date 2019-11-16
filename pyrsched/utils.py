from flask import make_response

def empty_response():
    res = make_response('', 204)
    res.headers = {} 
    res.content_length = 0
    return res
