import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent.resolve()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def main():
    print("=" * 65)
    print("  WIND TURBINE PREDICTIVE MAINTENANCE: NBM DASHBOARD")
    print("=" * 65)
    print(f"Serving dashboard locally from: {DIRECTORY}")
    print(f"URL: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server.")
    print("=" * 65)
    
    webbrowser.open(f"http://localhost:{PORT}")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down dashboard server.")

if __name__ == "__main__":
    main()
