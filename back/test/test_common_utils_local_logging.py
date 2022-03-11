import pytest
from service.logger.service_logger import ServiceLogger
from common.utils.local_logging import LLogging

from flaskapp.mpa_analysis_tool import create_app

@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api

def test_logging(api):
    logging_queue = ServiceLogger.instance().queue
    configurer = ServiceLogger.instance().worker_configurer

    llogger = LLogging(logging_queue, configurer)
    llogger.debug('debug')  # 통합 시스템로그 파일에만 저장됨
    llogger.warn('warn')
    llogger.warning('warning')
    llogger.info('info')
    llogger.critical('critical')
    llogger.error('error')

    llogger.set_filename('testlog')  # 확장자 제외한 파일명 입력. 이 시점 이후부터의 로그는 통합 시스템로그 + 개별 filename.log에 저장됨
    llogger.set_filepath('testlog')
    llogger.debug('debug')  # 통합 시스템로그 파일에만 저장됨
    llogger.warn('warn')
    llogger.warning('warning')
    llogger.info('info')
    llogger.critical('critical')
    llogger.error('error')