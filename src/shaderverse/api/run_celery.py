import argparse
import sys
import os
SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
sys.path.append(SCRIPT_PATH) # this is a hack to make the import work in Blender
from main import celery
import tempfile
from pathlib import Path
import logging

app = celery
def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Python script to bootstrap Celery')

    parser.add_argument('--concurrency',
                        help='number of workers', 
                        dest='concurrency', type=int, required=False,
                        default=4)
    
    python_args = sys.argv[sys.argv.index("--")+1:]
    args, unknown = parser.parse_known_args(args=python_args)
    return args

    

if __name__ == '__main__':
    tempdir = Path(tempfile.gettempdir())
    temp_file_name = f"celery_{next(tempfile._get_candidate_names())}.log"
    temp_file_path = tempdir.joinpath(temp_file_name)
    print(f"Logging to {temp_file_path}")
    args = get_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(message)s')

    # worker = app.Worker(
    #     loglevel='INFO',
    #     concurrency=args.concurrency,
    #     pool='solo',
    #     logfile=str(temp_file_path)
    # )

    worker = app.Worker(
        loglevel='INFO',
        concurrency=args.concurrency,
        pool='solo'
    )
    


    worker.start()