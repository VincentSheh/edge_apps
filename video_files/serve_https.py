import http.server
import ssl

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'x-api-key, Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')        
        return super(CORSRequestHandler, self).end_headers()

httpd = http.server.HTTPServer(("0.0.0.0", 8010), CORSRequestHandler)
#httpd.socket = ssl.wrap_socket(httpd.socket,
#                               keyfile="localhost+3-key.pem",
#                               certfile="localhost+3.pem", server_side=True)

print("Serving on https://0.0.0.0:8010")
httpd.serve_forever()

