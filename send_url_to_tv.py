import soco
import logging
import socket

# Logging-Setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DLNA')

def find_tv_by_name_or_ip(identifier):
    logger.info(f"Searching for device with identifier: {identifier}")
    devices = soco.discover()
    if devices:
        for device in devices:
            logger.info(f"Found device: {device.player_name} with IP: {device.ip_address}")
            if device.player_name == identifier or device.ip_address == identifier:
                return device
    return None

def send_url_to_tv(tv, url):
    try:
        tv.play_uri(url)
        logger.info(f"URL {url} successfully sent to TV")
    except Exception as e:
        logger.error(f"Failed to send URL to TV: {e}")

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

if __name__ == "__main__":
    device_identifier = 'Ok - tv'  # This can be either the device name or IP address
    device = find_tv_by_name_or_ip(device_identifier)
    if device:
        logger.info(f"Found device: {device.player_name} with IP: {device.ip_address}")
        url = 'http://example.com'
        send_url_to_tv(device, url)
    else:
        logger.error(f"No device found with identifier {device_identifier}")

    computer_identifier = '192.168.0.216'  # This can be either the computer name or IP address
    command = 'xdg-open http://192.168.0.61:50000/Folie1.PNG'
    send_command_to_computer(computer_identifier, command)