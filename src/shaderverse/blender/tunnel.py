from pyngrok import ngrok

http_tunnel = None


class Tunnel():
    alive: bool

    def __init__(self):
        self.process = ngrok.connect(8118, "http")
        self.subdomain = self.get_subdomain(self.process.public_url)
        self.alive = True
        print(self.subdomain)

    def get_subdomain(self, uri: str)-> str:
        subdomain = uri.replace("http://", "")
        subdomain = subdomain.split(".")[0]
        return subdomain
    
    def kill(self):
        ngrok.kill()
        self.alive = False


def start():
    global http_tunnel
    http_tunnel = Tunnel()

if __name__ == "__main__":
    start()
