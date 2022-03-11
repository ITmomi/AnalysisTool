class LLogging:
    def __init__(self, queue, configurer):
        self.logger = configurer(queue)
        self.file = None
        self.path = None

    def set_filename(self, filename):
        self.file = filename

    def set_filepath(self, filepath):
        self.path = filepath

    def debug(self, msg):
        if self.file is not None:
            self.logger.debug(msg, extra={'file': self.file, 'path': self.path})
        else:
            self.logger.debug(msg)

    def warning(self, msg):
        if self.file is not None:
            self.logger.warning(msg, extra={'file': self.file, 'path': self.path})
        else:
            self.logger.warning(msg)

    def warn(self, msg):
        if self.file is not None:
            self.logger.warn(msg, extra={'file': self.file, 'path': self.path})
        else:
            self.logger.warn(msg)

    def critical(self, msg):
        if self.file is not None:
            self.logger.critical(msg, extra={'file': self.file, 'path': self.path})
        else:
            self.logger.critical(msg)

    def info(self, msg):
        if self.file is not None:
            self.logger.info(msg, extra={'file': self.file, 'path': self.path})
        else:
            self.logger.info(msg)

    def error(self, msg):
        if self.file is not None:
            self.logger.error(msg, extra={'file': self.file, 'path': self.path})
        else:
            self.logger.error(msg)
