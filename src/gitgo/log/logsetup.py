import logging
import sys
from pathlib import Path

import os

Logger = logging.Logger


logging.basicConfig(format='%(levelname)s:%(message)s\n', level=logging.DEBUG)

# Set up logging for our application.
logdir = os.getenv('LOGDIR', None)
if logdir:
    os.makedirs(logdir, exist_ok=True)
    logfile = Path(logdir) / os.getenv('LOGFILE', 'git.log')
    logging.basicConfig(filename=logfile,
                        format='%(asctime)s %(levelname)s:%(message)s\n', level=logging.DEBUG)
log = logging.getLogger(__name__)
error_log = logging.StreamHandler(sys.stderr)
error_log.setLevel(logging.ERROR)
log.addHandler(error_log)
std_log = logging.StreamHandler(sys.stdout)
std_log.setLevel(logging.INFO)
log.addHandler(std_log)

__all__ = ['log', 'error_log', 'std_log', 'Logger']

