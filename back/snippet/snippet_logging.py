from service.logger.service_logger import ServiceLogger
from common.utils.local_logging import LLogging
from multiprocessing import Process


def foo(logging_queue, configurer):
    llogger = LLogging(logging_queue, configurer)
    llogger.info('local_run start')   # 통합 시스템로그 파일에만 저장됨

    llogger.set_filename('filename')  # 확장자 제외한 파일명 입력. 이 시점 이후부터의 로그는 통합 시스템로그 + 개별 filename.log에 저장됨
    llogger.set_filepath('/path')


if __name__ == '__main__':
    logging_queue = ServiceLogger.instance().queue
    configurer = ServiceLogger.instance().worker_configurer

    process = Process(target=foo, args=(logging_queue, configurer))
