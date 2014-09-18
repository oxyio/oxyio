# Oxypanel
# File: util/log.py
# Desc: logging utilities

import logging

import coloredlogs

import config


logger = logging.getLogger('oxypanel')

log_args = {
    'show_timestamps': False,
    'show_hostname': False
}

if config.DEBUG:
    coloredlogs.install(level=logging.DEBUG, **log_args)
    logger.debug('Debug enabled')
else:
    coloredlogs.install(level=logging.CRITICAL, **log_args)

def critical(*args):
    for arg in args:
        logger.critical(arg)

def error(*args):
    for arg in args:
        logger.error(arg)

def warning(*args):
    for arg in args:
        logger.warning(arg)

def info(*args):
    for arg in args:
        logger.info(arg)

def debug(*args):
    for arg in args:
        logger.debug(arg)
