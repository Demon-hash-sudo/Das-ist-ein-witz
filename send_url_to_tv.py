import logging
import socket
import time
import requests
import subprocess

# Logging-Setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DLNA')

def find_tv_by_ip(ip_address):
    logger.info(f"Checking device at IP: {ip_address}")
    try:
        response = requests.get(f"http://{ip_address}:1400/xml/device_description.xml", timeout=5)
        if response.status_code == 200:
            logger.info(f"Found device at IP: {ip_address}")
            return ip_address
    except requests.RequestException as e:
        logger.error(f"Failed to connect to device at IP: {ip_address}: {e}")
    return None

def send_url_to_tv(ip_address, url):
    try:
        # Assuming the TV supports the AVTransport service
        av_transport_url = f"http://{ip_address}:1400/MediaRenderer/AVTransport/Control"
        headers = {'Content-Type': 'text/xml; charset="utf-8"', 'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'}
        body = f"""<?xml version="1.0" encoding="utf-8"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body>
                <u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
                    <InstanceID>0</InstanceID>
                    <CurrentURI>{url}</CurrentURI>
                    <CurrentURIMetaData></CurrentURIMetaData>
                </u:SetAVTransportURI>
            </s:Body>
        </s:Envelope>"""
        response = requests.post(av_transport_url, headers=headers, data=body)
        if response.status_code == 200:
            logger.info(f"URL {url} successfully sent to TV at {ip_address}")
            # Wait for a few seconds to ensure the image is loaded
            time.sleep(3)
            # Pause the TV to "freeze" the image
            pause_tv(ip_address)
        else:
            logger.error(f"Failed to send URL to TV: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send URL to TV: {e}")

def pause_tv(ip_address):
    try:
        av_transport_url = f"http://{ip_address}:1400/MediaRenderer/AVTransport/Control"
        headers = {'Content-Type': 'text/xml; charset="utf-8"', 'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#Pause"'}
        body = """<?xml version="1.0" encoding="utf-8"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body>
                <u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
                    <InstanceID>0</InstanceID>
                </u:Pause>
            </s:Body>
        </s:Envelope>"""
        response = requests.post(av_transport_url, headers=headers, data=body)
        if response.status_code == 200:
            logger.info(f"TV at {ip_address} paused to freeze the image")
        else:
            logger.error(f"Failed to pause TV: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to pause TV: {e}")

def send_command_to_computer(computer_identifier, command):
    try:
        # Resolve the computer name to an IP address if necessary
        try:
            computer_ip = socket.gethostbyname(computer_identifier)
        except socket.gaierror:
            computer_ip = computer_identifier  # Assume it's already an IP address

        port = 65432  # The port used by the server on the other computer

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((computer_ip, port))
            s.sendall(command.encode())
            logger.info(f"Command '{command}' successfully sent to {computer_identifier}")
    except Exception as e:
        logger.error(f"Failed to send command to {computer_identifier}: {e}")

def maximize_and_freeze_screen():
    try:
        # Maximize the window (this command may vary depending on the system and window manager)
        subprocess.run(['xdotool', 'search', '--onlyvisible', '--class', 'firefox', 'windowactivate', '--sync', 'key', 'F11'])
        logger.info("Window maximized")
        # Wait for 5 seconds
        time.sleep(5)
        # Freeze the screen (this command may vary depending on the system)
        subprocess.run(['xdotool', 'search', '--onlyvisible', '--class', 'firefox', 'windowactivate', '--sync', 'key', 'Ctrl+Shift+S'])
        logger.info("Screen frozen")
    except Exception as e:
        logger.error(f"Failed to maximize and freeze screen: {e}")

if __name__ == "__main__":
    device_ip = '192.168.0.71'  # This is the IP address of the TV
    device = find_tv_by_ip(device_ip)
    if device:
        url = 'http://192.168.0.61:50000/Folie1.PNG'
        send_url_to_tv(device, url)
    else:
        logger.error(f"No device found with IP {device_ip}")

    computer_identifier = '192.168.0.216'  # This can be either the computer name or IP address
    command = 'xdg-open http://192.168.0.61:50000/Folie1.PNG && sleep 3 && xdotool search --onlyvisible --class firefox windowactivate --sync key F11 && sleep 5 && xdotool search --onlyvisible --class firefox windowactivate --sync key Ctrl+Shift+S'
    send_command_to_computer(computer_identifier, command)