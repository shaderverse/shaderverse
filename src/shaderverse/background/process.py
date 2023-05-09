import subprocess
from enum import Enum   

class Status(str, Enum):
    """Status of the fetch"""
    pending="pending"
    running="running"
    completed="completed"

class Process:
    """ Run the process in the background 
    Parameters
    ----------
    cmd: list[str]
        The command to run"""

 
    status: status = Status.pending
    process: subprocess.Popen[bytes] = None
     
    def __init__(self, cmd: list[str] = None):

        self.status = Status.pending

        if cmd is not None:
            self.cmd = cmd

    def execute(self):
        """Run the process"""
        if self.cmd is None:
            raise ValueError("Command not set")

        print(f"Running command: {self.cmd}")
        self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, shell=True)
        self.result = ""       


    @property
    def status(self):
        return self._status
    
    @status.setter      
    def status(self, value: Status):
        try:
            Status(value)
            self._status = value
        except ValueError:
            raise ValueError(f"Invalid status: {value}")
        
    @property
    def cmd(self):
        return self._cmd
    
    @cmd.setter
    def cmd(self, value: list[str]):
        """Set the cmd of the process"""
        self._cmd = value
    

    def refresh_result(self):
        """ Refresh the result of the process"""
        outs = None
        try:
            outs, errs = self.process.communicate(timeout=0.1)
            self.status = Status.completed
            if outs:
                self.result = outs.decode().strip()
        except subprocess.TimeoutExpired:
            self.status = Status.running
            # outs, errs = self.process.communicate()
        

    @property
    def result(self):
        if self.process:
            self.refresh_result()
        return self._result
    
    @result.setter
    def result(self, value):
        self._result = value    