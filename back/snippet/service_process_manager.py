from multiprocessing import Lock


class ProcessManager:
    _instance = None

    @classmethod
    def _get_instance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls._get_instance
        return cls._instance

    def __init__(self):
        self.processes = []
        self.lock = Lock()

    def append_proc(self, proc):
        self.lock.acquire()

        self.processes.append(proc)

        self.lock.release()

    def get_procs(self):
        return self.processes.copy()

    def delete_proc(self, target):

        target.terminate()
        target.join()
        target.close()

        self.lock.acquire()

        for proc in self.processes:
            if proc == target:
                self.processes.remove(proc)

        self.lock.release()

    def check_process(self):
        print('check_process', self.processes)
        for proc in self.processes:
            print(proc.is_alive())
