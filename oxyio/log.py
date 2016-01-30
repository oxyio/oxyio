# oxy.io
# File: oxyio/log.py
# Desc: logging utilities & system log

import logging

import coloredlogs

from oxyio import settings


logger = logging.getLogger('oxyio')

# Setup colored logs & debug error pages
log_args = {
    'show_timestamps': False,
    'show_hostname': False
}

if settings.DEBUG:
    coloredlogs.install(level=logging.DEBUG, **log_args)
    logger.debug('Debug enabled')
else:
    coloredlogs.install(level=logging.CRITICAL, **log_args)

# Hide some core loggers
logging.getLogger('werkzeug').setLevel(level=logging.CRITICAL)
logging.getLogger('requests').setLevel(level=logging.CRITICAL)
logging.getLogger('urllib3').setLevel(level=logging.CRITICAL)
logging.getLogger('elasticsearch').setLevel(level=logging.CRITICAL)
