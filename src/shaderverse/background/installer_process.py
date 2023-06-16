from .process import Process
import sys
from pathlib import Path

class Installer(Process):
    script_path = Path(__file__).parent.absolute()
    installer_path = Path(Path(script_path).parent.absolute(), "background", "installer_runner.py")

    def __init__(self, binary_name: str, windows_url: str, macosx64_url: str, macossilicon_url:str, linux_url: str, windows_binary_file: str = None, macosx64_binary_file: str = None, macossilicon_binary_file: str = None, linux_binary_file: str = None ):
        cmd = [sys.executable, self.installer_path, '--binary_name', binary_name, '--windows_url', windows_url, '--macosx64_url', macosx64_url, '--macossilicon_url', macossilicon_url, '--linux_url', linux_url]
        if windows_binary_file:
            cmd.extend(['--windows_binary_file', windows_binary_file])
        if macosx64_binary_file:
            cmd.extend(['--macosx64_binary_file', macosx64_binary_file])
        if macossilicon_binary_file:
            cmd.extend(['--macossilicon_binary_file', macossilicon_binary_file])
        if linux_binary_file:
            cmd.extend(['--linux_binary_file', linux_binary_file])
        super().__init__(cmd)
        