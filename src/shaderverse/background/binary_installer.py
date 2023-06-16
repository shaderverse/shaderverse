import os
import platform
import requests
import zipfile
import tarfile
from pathlib import Path
from tempfile import gettempdir
import stat

def get_temporary_directory(directory_name: str = 'tmp') -> Path:
    if platform.system() == 'Windows':
        temp_dir = Path(gettempdir())
    else:
        temp_dir = Path(gettempdir()) / directory_name

    temp_dir.mkdir(parents=True, exist_ok=True)

    return temp_dir

class BinaryInstaller:
    def __init__(self, binary_name:str, windows_url: str, macosx64_url: str, macossilicon_url:str, linux_url: str, windows_binary_file: str = None, macosx64_binary_file: str = None, macossilicon_binary_file: str = None, linux_binary_file: str = None):
        self.urls = {
            'windows': windows_url,
            'macosx64': macosx64_url,
            'macossilicon': macossilicon_url,
            'linux': linux_url
        }

        self.files = {
            'windows': windows_binary_file,
            'macosx64': macosx64_binary_file,
            'macossilicon': macossilicon_binary_file,
            'linux': linux_binary_file
        }

        # if windows_binary_file:
        #     self.binary_files['windows'] = windows_binary_file
        # if macosx64_binary_file:
        #     self.binary_files['macosx64'] = macosx64_binary_file
        # if macossilicon_binary_file:
        #     self.binary_files['macossilicon'] = macossilicon_binary_file
        # if linux_binary_file:
        #     self.binary_files['linux'] = linux_binary_file

        self.binary_name = binary_name

    def detect_os(self):
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

    def download_binary(self, url, target_path):
        response = requests.get(url, stream=True)
        with open(target_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    def extract_archive(self, archive_path, target_dir):
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz') or archive_path.endswith('.tar.xz'):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(target_dir)

    def get_extesion(self, url):
        if url.endswith('.zip'):
            return '.zip'
        elif url.endswith('.tar.gz') or url.endswith('.tgz'):
            return '.tar.gz'
        elif url.endswith('.tar.xz'):
            return '.tar.xz'

    def install_binary(self):
        os_name = self.detect_os()
        if os_name is None:
            print("Unsupported operating system.")
            return

        
        
        shaderverse_dir = os.path.join(os.path.expanduser("~"), ".shaderverse")
        binary_install_dir = os.path.join(shaderverse_dir, self.binary_name)
        binary_file = self.files.get(os_name)
        binary_path = Path(binary_install_dir, binary_file)

        if binary_path.exists() == False:
            binary_url = self.urls.get(os_name)
            if binary_url is None:
                print("Binary URL not provided for the detected operating system.")
                return  
            
            archive_extension = self.get_extesion(binary_url)

            # Download binary to a temporary directory
            # temp_dir = os.path.join(os.path.expanduser("~"), f"{self.binary_name}_temp")
            temp_dir = get_temporary_directory()
            os.makedirs(temp_dir, exist_ok=True)
            binary_archive_path = os.path.join(temp_dir, f"{self.binary_name}_archive{archive_extension}")
            self.download_binary(binary_url, binary_archive_path)
            print(f"Downloaded {self.binary_name} to {binary_archive_path}")

            # Install binary to the user's home directory
            
            os.makedirs(shaderverse_dir, exist_ok=True)
            
            self.extract_archive(binary_archive_path, binary_install_dir)

            # Make binary executable
            
            binary_path.chmod(binary_path.stat().st_mode | stat.S_IEXEC)


            # Clean up temporary files
            # os.remove(binary_archive_path)

            print(f"{self.binary_name} installed successfully to {binary_install_dir}")
        else:    
            print(f"{self.binary_name} is already installed at {binary_install_dir}")