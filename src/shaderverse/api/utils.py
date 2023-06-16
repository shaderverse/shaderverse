import platform
from tempfile import gettempdir
from pathlib import Path

def get_temporary_directory(directory_name: str = 'tmp') -> Path:
    if platform.system() == 'Windows':
        temp_dir = Path(gettempdir())
    else:
        temp_dir = Path(gettempdir()) / directory_name

    temp_dir.mkdir(parents=True, exist_ok=True)

    return temp_dir

def get_os():
    """Get the current operating system"""  
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin" and platform.machine() == "x86_64":
        return "macosx64"
    elif system == "Darwin" and platform.machine() == "arm64":
        return "macossilicon"
    elif system == "Linux":
        return "linux"
    else:
        return None