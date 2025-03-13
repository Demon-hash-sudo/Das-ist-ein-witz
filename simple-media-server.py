from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import logging
import sys
import subprocess

# Logging-Setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WebServer')

def get_network_info():
    """Sammelt Netzwerk-Informationen für Debugging"""
    info = []
    try:
        # Windows ipconfig ausführen
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        info.append("=== Network Interfaces ===")
        info.append(result.stdout)
        
        # Aktive Verbindungen anzeigen
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        info.append("=== Active Connections ===")
        info.append(result.stdout)
    except Exception as e:
        info.append(f"Error getting network info: {e}")
    return '\n'.join(info)

class DebugHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Überschreibe log_message für detaillierteres Logging"""
        logger.info(f"{self.address_string()} - {format%args}")

# Niedrigere Ports testen
PORTS = [50000, 8080, 8000]

for port in PORTS:
    try:
        # Zeige Netzwerk-Diagnose
        print(get_network_info())
        
        server = HTTPServer(('', port), DebugHandler)
        print(f"\n=== Server gestartet auf Port {port} ===")
        print(f"Versuchen Sie diese URLs:")
        
        # Alle möglichen IPs anzeigen
        hostname = socket.gethostname()
        try:
            ips = socket.gethostbyname_ex(hostname)[2]
            for ip in ips:
                if not ip.startswith('127.'):
                    print(f"http://{ip}:{port}")
        except:
            pass
        
        print(f"\nLokal: http://localhost:{port}")
        print("Strg+C zum Beenden\n")
        
        server.serve_forever()
        break
    except Exception as e:
        logger.error(f"Port {port} nicht verfügbar: {e}")
        continue