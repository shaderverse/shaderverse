import subprocess
import os
from enum import Enum   

class Status(str, Enum):
    """Status of the fetch"""
    pending="pending"
    running="running"
    completed="completed"

class Method(str, Enum):
    """Method of the fetch"""
    GET="GET"
    POST="POST"
    PUT="PUT"
    DELETE="DELETE"

class Fetch:
    """Fetch class to make requests in the backend 
    Parameters 
    ----------
    url: str
        The url to make the request
    method: Method
        The method of the request
    json_file: str
        The json file to send in the request
    """
    
    url: str = None
    status: status = Status.pending
    process = None
     
    def __init__(self, url: str = None, method: Method = "POST", json_file: str = None):
        self.method = method
        self.json_file = json_file
        self.result = None
        self.status = Status.pending

        if url is not None:
            self.url = url

    def make_request(self):
        """Make the request to the backend using the http_request.py script"""
        if self.url is None:
            raise ValueError("Url not set")
        cmd = ["python", "http_request.py", "--url", self.url, "--method", self.method]
        data_cmd = [] if  self.json_file is None else ["--json", self.json_file]
        cmd = cmd + data_cmd
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        self.result = ""       

    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, value):
        """Set the url of the fetch"""
        if not value.startswith("http"):
            raise ValueError(f"Invalid url: {value}")
        self._url = value
    
    @property
    def method(self):
        return self._method
    
    @method.setter
    def method(self, value: Method):
        try:
            Method(value)
            self._method = value
        except ValueError:
            raise ValueError(f"Invalid method: {value}")
        
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
    def json_file(self):
        return self._json_file
    
    @json_file.setter
    def json_file(self, value):
        if value and not os.path.exists(value):
            raise ValueError(f"Invalid json file: {value}")
        self._json_file = value

    def refresh_result(self):
        """ Refresh the result of the fetch from the subprocess"""
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