import importlib
import logging.handlers
import multiprocessing
import os
import sys

from service.logger.service_logger import ServiceLogger
from service.cleaner.service_cleaner import ServiceCleaner
from common.utils import migration

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + os.path.sep
sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)


def initialize_log(app):
    logging_queue = ServiceLogger.instance().queue
    listener = multiprocessing.Process(target=ServiceLogger.instance().logging_process,
                                       args=(logging_queue, app.config['DEBUG'], os.getpid()))
    listener.daemon = True
    listener.start()

    handler = logging.handlers.QueueHandler(logging_queue)  # Just the one handler needed
    logger = logging.getLogger(app.config['LOG'])
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger_werkzeug = logging.getLogger('werkzeug')
    logger_werkzeug.addHandler(handler)


if __name__ == '__main__':
    config_file = '../config/app_config.py'

    if os.environ.get('CRAS_SERVER') is None:
        module_name = 'flaskapp.mpa_analysis_tool'
    else:
        module_name = 'flaskapp.cras_server'

    module = importlib.import_module(module_name)
    creator = getattr(module, 'create_app')

    app = creator(config_file)

    if len(sys.argv) > 1:
        if sys.argv[1] == 'release':
            app.config['DEBUG'] = False

    initialize_log(app)

    migration.migration_db()

    service_cleaner = ServiceCleaner()
    service_cleaner.setDaemon(True)
    service_cleaner.start()

    app.run(threaded=True, host='0.0.0.0')
