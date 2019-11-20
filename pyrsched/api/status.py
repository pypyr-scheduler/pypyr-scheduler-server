import apscheduler
import logging

from flask import current_app

logger = logging.getLogger(__name__)


def get():
    logger.info('GET /status')
    return {
        'is_running': current_app.scheduler.state != apscheduler.schedulers.base.STATE_STOPPED,
    }
