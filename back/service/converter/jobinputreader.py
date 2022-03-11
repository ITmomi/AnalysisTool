from multiprocessing import Process


class JobInputReader:

    def __init__(self, name, config, queue):
        self.name = name
        self.config = config
        self.queue = queue
        process = Process(target=self.worker, args=(config, queue))
        process.name = name
        process.start()
        pass

    def exists(self) -> bool:
        pass

    def get(self) -> str:
        pass

    def worker(self, config, queue):
        pass


class JobInputReaderRuntimeException(Exception):
    pass
