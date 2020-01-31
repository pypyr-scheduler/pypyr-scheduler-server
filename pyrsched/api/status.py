import apscheduler
import logging

from flask import current_app

logger = logging.getLogger(__name__)

def get():
    logger.info('GET /status')
    state = {
        'is_running': False,
        'message': None,
    }
    try:
        connstate = current_app.scheduler.root.state()
        state['is_running'] = connstate != apscheduler.schedulers.base.STATE_STOPPED
        state['message'] = 'connected'
    except Exception:
        state['is_running'] = False
        state['message'] = 'no connection to server'
    return state
