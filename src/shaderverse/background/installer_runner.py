import argparse
import sys
import os
SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
sys.path.append(SCRIPT_PATH) # this is a hack to make the import work in Blender
from pathlib import Path
import logging
from binary_installer import BinaryInstaller

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Python script to install binaries')

    parser.add_argument('--binary_name',
                        help='binary_name', 
                        dest='binary_name', type=str, required=True)
    
    parser.add_argument('--windows_url',
                        help='windows_url', 
                        dest='windows_url', type=str, required=True)
    
    parser.add_argument('--macosx64_url',
                        help='macosx64_url', 
                        dest='macosx64_url', type=str, required=True)
    
    parser.add_argument('--macossilicon_url',
                        help='macossilicon_url', 
                        dest='macossilicon_url', type=str, required=True)
    
    parser.add_argument('--linux_url',
                        help='linux_url', 
                        dest='linux_url', type=str, required=True)
    
    parser.add_argument('--windows_binary_file',
                        help='windows_binary_file', 
                        dest='windows_binary_file', type=str, required=False)
    
    parser.add_argument('--macosx64_binary_file',
                        help='macosx64_binary_file', 
                        dest='macosx64_binary_file', type=str, required=False)
    
    parser.add_argument('--macossilicon_binary_file',
                        help='macossilicon_binary_file', 
                        dest='macossilicon_binary_file', type=str, required=False)

    parser.add_argument('--linux_binary_file',
                        help='linux_binary_file', 
                        dest='linux_binary_file', type=str, required=False)


    args, unknown = parser.parse_known_args()
    return args

if __name__ == '__main__':
    args = get_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(message)s')
    installer = BinaryInstaller( args.binary_name, args.windows_url, args.macosx64_url, args.macossilicon_url, args.linux_url, args.windows_binary_file, args.macosx64_binary_file, args.macossilicon_binary_file, args.linux_binary_file)
    installer.install_binary()
