from pyngrok import ngrok

http_tunnel = None
class Tunnel():
    """ Provides ngrok tunnelling for Blender"""
    alive: bool

    def __init__(self):
        """ Start the tunnel on port 8118 """
        self.process = ngrok.connect(8118, "http")
        self.subdomain = self.get_subdomain(self.process.public_url)
        self.alive = True
        print(f"Started tunnel: {self.subdomain}")

    def get_subdomain(self, uri: str)-> str:
        """ Get subdomain from public ngrok url """
        subdomain = uri.replace("http://", "")
        subdomain = subdomain.split(".")[0]
        return subdomain
    
    def kill(self):
        """ Kill all ngrok processes """
        ngrok.kill()
        self.alive = False
        print(f"Started tunnel: {self.subdomain}")


def start():
    global http_tunnel
    http_tunnel = Tunnel()

if __name__ == "__main__":
    start()
