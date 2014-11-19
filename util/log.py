# Oxypanel
# File: util/log.py
# Desc: logging utilities & system log

import logging

import coloredlogs

import config


logger = logging.getLogger('oxypanel')


# Setup colored logs & debug error pages
log_args = {
    'show_timestamps': False,
    'show_hostname': False
}

if config.DEBUG:
    coloredlogs.install(level=logging.DEBUG, **log_args)
    logger.debug('Debug enabled')
else:
    coloredlogs.install(level=logging.CRITICAL, **log_args)
