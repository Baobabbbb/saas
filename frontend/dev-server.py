"""
Serveur de développement simple pour tester l'interface frontend
"""

import http.server
import socketserver
import os
import webbrowser
from threading import Timer

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_dev_server():
    PORT = 5173
    
    # Changer vers le répertoire frontend
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = CORSHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Serveur de développement démarré sur http://localhost:{PORT}")
        print(f"📁 Répertoire: {os.getcwd()}")
        print(f"🎬 Interface: http://localhost:{PORT}/animation-generator.html")
        print("Press Ctrl+C to stop")
        
        # Ouvrir automatiquement le navigateur
        Timer(1.0, lambda: webbrowser.open(f'http://localhost:{PORT}/animation-generator.html')).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Serveur arrêté")

if __name__ == "__main__":
    start_dev_server()
