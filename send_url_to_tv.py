import soco
import logging
import socket

# Logging-Setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DLNA')

def find_tv_by_name(name):
    device = soco.discovery.by_name(name)
    if device and device.is_visible:
        return device
    return None

def send_url_to_tv(tv, url):
    try:
        tv.play_uri(url)
        logger.info(f"URL {url} successfully sent to TV")
    except Exception as e:
        logger.error(f"Failed to send URL to TV: {e}")

def send_command_to_computer(computer_name, command):
    try:
        # Resolve the computer name to an IP address
        computer_ip = socket.gethostbyname(computer_name)
        port = 65432  # The port used by the server on the other computer

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((computer_ip, port))
            s.sendall(command.encode())
            logger.info(f"Command '{command}' successfully sent to {computer_name}")
    except Exception as e:
        logger.error(f"Failed to send command to {computer_name}: {e}")

if __name__ == "__main__":
    device_name = 'Ok - tv'
    device = find_tv_by_name(device_name)
    if device:
        logger.info(f"Found device: {device.player_name}")
        url = 'http://example.com'
        send_url_to_tv(device, url)
    else:
        logger.error(f"No device found with name {device_name}")

    computer_name = 'other-computer'
    command = 'open http://example.com'
    send_command_to_computer(computer_name, command)