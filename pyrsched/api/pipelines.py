import logging
from pathlib import Path

from flask import current_app, send_file
from werkzeug.utils import secure_filename

from ..utils import empty_response, make_target_filename

logger = logging.getLogger(__name__)


def get_one(filename):
    """
    Return a specific pipeline.
    """
    logger.info(f'GET /pipelines/{filename}')

    filename = make_target_filename(filename)

    try:
        return send_file(filename, as_attachment=True, mimetype='application/x-yaml', attachment_filename='filename')
    except FileNotFoundError:
        return 'File not found', 404


def get_all():
    """
    Return a list of all known pipelines.
    """
    logger.info('GET /pipelines')
    base_path = Path(current_app.iniconfig.get('pipelines', 'base_path'))
    return [{'filename': p.name} for p in base_path.iterdir()]


def _save_file(filename, content, success_status=201):
    # make directory if it does not exist
    target = make_target_filename(filename)
    if not target.parent.exists():
        target.parent.mkdir(parents=True)
    logger.info(f'saving file contents to {target.resolve()}')
    # logger.debug(content)
    content.save(str(target))
    if success_status == 204:  # 204 NO CONTENT requires to send nothing, not even headers
        return empty_response()
    return 'OK, Pipeline was uploaded', success_status


def create(filename, body):
    logger.info(f'POST /pipelines/{filename}')
    if not filename == secure_filename(filename):
        logger.warning(f'Possible malicious filename detected: "{filename}"')
        return 'Not Acceptable, possible malicious content detected', 406
    return _save_file(filename, body)


def update(filename, body):
    logger.info(f'PUT /pipelines/{filename}')
    if not filename == secure_filename(filename):
        logger.warning(f'Possible malicious filename detected: "{filename}"')
        return 'Not Acceptable, possible malicious content detected', 406
    target_file = make_target_filename(filename)
    if not target_file.exists():
        return 'Pipeline not found', 404
    return _save_file(filename, body, success_status=204)


def delete(filename):
    logger.info(f'DELETE /pipelines/{filename}')
    if not filename == secure_filename(filename):
        logger.warning(f'Possible malicious filename detected: "{filename}"')
        return 'Not Acceptable, possible malicious content detected', 406
    target_file = make_target_filename(filename)
    try:
        target_file.unlink()
        return empty_response()
    except FileNotFoundError:
        return 'Pipeline not found', 404
