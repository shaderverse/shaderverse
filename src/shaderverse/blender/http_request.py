import argparse
import requests
import json


def make_request(url: str, method: str, data: dict = None) -> requests.Response:
    headers = {'Content-type': 'application/json'}
    if method == "GET":
        return requests.get(url)
    elif method == "POST":
        return requests.post(url, json=data, headers=headers)
    elif method == "PUT":
        return requests.put(url, json=data, headers=headers)
    elif method == "DELETE":
        return requests.delete(url)
    else:
        raise ValueError(f"Invalid method: {method}")
    
def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)
    

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Python script to make requests in the backe.')
    parser.add_argument('--method', 
                        help='the method', 
                        dest='method', type=str, default="POST")
    parser.add_argument('--url', 
                        help='the url', 
                        dest='url', type=str, required=True)
    parser.add_argument('--json', 
                        help='the json file', 
                        dest='json', type=str, default=None)
    return parser.parse_args()
    

if __name__ == "__main__":
    args = get_args()       
    data = load_json(args.json) if args.json else None
    response = make_request(args.url, args.method, data)
    response_dict = response.json()
    print(json.dumps(response_dict))
