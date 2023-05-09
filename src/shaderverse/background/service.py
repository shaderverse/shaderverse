from .process import Process
import psutil

class Service(Process):
    def __init__(self, cmd: list[str] = None):
        super().__init__(cmd)

    def kill_process_recursively(self, process: psutil.Process):
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    def kill(self):
        global is_initialized
        process = psutil.Process(self.process.pid)
        self.kill_process_recursively(process)