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