from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import logging
import sys
import subprocess
import os

# Logging setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WebServer')

def parse_hex_ip(hex_ip):
    """Convert hex IP to readable format"""
    return '.'.join(str(int(hex_ip[i:i+2], 16)) for i in (6,4,2,0))

def parse_hex_port(hex_port):
    """Convert hex port to decimal"""
    return int(hex_port, 16)

def get_network_info():
    """Sammelt Netzwerk-Informationen für Debugging"""
    info = []
    try:
        # Get hostname and IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        info.append("=== Network Information ===")
        info.append(f"Hostname: {hostname}")
        info.append(f"Local IP: {local_ip}")
        
        # Read active connections from proc
        if sys.platform.startswith('linux'):
            info.append("\n=== Active TCP Connections ===")
            info.append("Local Address:Port         Remote Address:Port      State")
            with open('/proc/net/tcp', 'r') as f:
                # Skip header line
                next(f)
                for line in f:
                    parts = line.strip().split()
                    local_addr, local_port = parts[1].split(':')
                    remote_addr, remote_port = parts[2].split(':')
                    state = parts[3]
                    
                    local = f"{parse_hex_ip(local_addr)}:{parse_hex_port(local_port)}"
                    remote = f"{parse_hex_ip(remote_addr)}:{parse_hex_port(remote_port)}"
                    info.append(f"{local:<23} {remote:<23} {state}")
    except Exception as e:
        info.append(f"Error getting network info: {e}")
    return '\n'.join(info)

class DebugHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        client_ip = self.client_address[0]
        logger.info(f"GET request from {client_ip}: {self.path}")
        return super().do_GET()

def run_server(port=50000):
    server_address = ('0.0.0.0', port)
    try:
        httpd = HTTPServer(server_address, DebugHandler)
        # More permissive socket options
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Get all network interfaces
        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        all_ips = [ip[-1][0] for ip in interfaces]
        
        logger.info(f'Starting server on port {port}...')
        logger.info(f'Available on:')
        for ip in all_ips:
            logger.info(f'  http://{ip}:{port}')
        logger.info(f'  http://0.0.0.0:{port}')
        
        httpd.serve_forever()
    except PermissionError:
        logger.error(f"Permission denied. Try using a port number > 1024 or run with sudo")
        sys.exit(1)
    except OSError as e:
        logger.error(f"Network error: {e}")
        logger.debug("Try checking if port is already in use: ss -tulpn | grep {port}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info('Shutting down server...')
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    run_server(port)