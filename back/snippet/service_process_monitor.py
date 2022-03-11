import time
from threading import Thread
from snippet.service_process_manager import ProcessManager


class ProcessMonitor(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            procs = ProcessManager.instance().get_procs()

            print('length : ', len(procs))
            # print('daemon pid :', self.pid)
            for proc in procs:
                # print(proc.pid, proc.is_alive())
                if not proc.is_alive():
                    ProcessManager.instance().delete_proc(proc)

            time.sleep(1)
