from pathlib import Path

import click

from . import logger
from .server import ServerWrapper


@click.command()
@click.option("-c", "--conf", "conf_dir", default="conf", help="config directory")
def cli(conf_dir):
    click.echo(f"Starting scheduler. Config: {Path(conf_dir).resolve()}")
    server = ServerWrapper(conf_dir)
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit, ConnectionError) as e:
        logger.debug("Shutdown signal received.")
        # logger.exception(e)
    finally:
        logger.info("Shutting down scheduler.")
        server.shutdown()
        logger.debug("Scheduler shutdown complete.")
