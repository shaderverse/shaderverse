import uvicorn
import json
import argparse




# with open(Path(base_path, 'config/config.json'), 'r') as f:
#     config = json.load(f)

# https://www.uvicorn.org/settings/


parser = argparse.ArgumentParser(description='Python script to bootstrap Uvicorn')

parser.add_argument('--app', 
                    help='the app')

parser.add_argument('--module', 
                    help='the module',
                    default="app")

parser.add_argument('--host', 
                    help='the ip addreess', 
                    default="0.0.0.0")

parser.add_argument('--port', 
                    help='the port', 
                    default=8118)

parser.add_argument('--reload', 
                    help='whether we should reload',
                    action='store_false')

parser.add_argument('--debug', 
                    help='run in debug mode?',
					action='store_false')

parser.add_argument('--workers', 
                    help='number of workers',
                    default=3)

args = parser.parse_args()

print("starting uvicorn")


uvicorn.run(app=args.app , host=args.host, port=args.port, reload=args.reload, debug=args.debug, workers=args.workers)

