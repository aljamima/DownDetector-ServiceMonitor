#!/usr/bin/python3
"""  
Network monitoring script that checks the availability of various services
and sends notifications to Slack when services go down or come back up.
"""

import json
import socket
import time
import _thread
from datetime import datetime
from urllib import request, parse

# Configuration dictionaries
SERVICES = {
    "zoomhash.io": {"port": 80},
    "airportshops.ddns.net": {"port": 22},
    "entiat.ddns.net": {"port": 22},
    "division.ddns.net": {"port": 710},
    "columbia.ddns.net": {"port": 710}
}

# Initialize failure counters
failure_counters = {service: 0 for service in SERVICES}

# Configuration constants
SLACK_WEBHOOK_URL = "REDACTED"
FAILURE_THRESHOLD = 3  # Number of consecutive failures before alerting
CHECK_INTERVAL = 30    # Seconds between service checks
RECOVERY_INTERVAL = 5  # Seconds between recovery checks
CONNECTION_TIMEOUT = 0.2  # Seconds for connection timeout

def check_service(hostname, port, timeout=CONNECTION_TIMEOUT):
    """
    Check if a service is responding on the specified port.
    
    Args:
        hostname (str): The hostname to check
        port (int): The port number to check
        timeout (float): Connection timeout in seconds
        
    Returns:
        bool: True if service is up, False otherwise
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    
    try:
        sock.connect((hostname, port))
        print(f"Service OK: {hostname}:{port}")
        return True
    except socket.timeout:
        print(f"Timeout for: {hostname}:{port}")
        return False
    except socket.error:
        print(f"Failed to connect to {hostname}:{port}")
        return False
    finally:
        sock.close()

def send_slack_notification(message):
    """
    Send a notification to Slack.
    
    Args:
        message (str): The message to send
    """
    payload = {"text": message}
    
    try:
        json_data = json.dumps(payload)
        req = request.Request(
            SLACK_WEBHOOK_URL,
            data=json_data.encode('ascii'),
            headers={'Content-Type': 'application/json'}
        )
        request.urlopen(req)
    except Exception as error:
        print(f"Failed to send Slack notification: {error}")

def monitor_service(hostname):
    """
    Monitor a service until it comes back up.
    
    Args:
        hostname (str): The hostname to monitor
    """
    while True:
        failure_counters[hostname] = 0
        time.sleep(RECOVERY_INTERVAL)
        
        if check_service(hostname, SERVICES[hostname]["port"]):
            current_time = datetime.utcnow()
            message = f"{current_time} -- Service is back UP for: {hostname}"
            send_slack_notification(message)
            break

def main():
    """Main monitoring loop."""
    while True:
        current_time = datetime.utcnow()
        
        for hostname, service_info in SERVICES.items():
            if not check_service(hostname, service_info["port"]):
                failure_counters[hostname] += 1
                
                if failure_counters[hostname] > FAILURE_THRESHOLD:
                    message = (f"{current_time} -- Outage detected at {hostname} "
                             f"(port: {service_info['port']})")
                    send_slack_notification(message)
                    failure_counters[hostname] = 0
                    _thread.start_new_thread(monitor_service, (hostname,))
            else:
                failure_counters[hostname] = 0
        
        # Reset counters at the start of each hour
        if current_time.minute == 0:
            for hostname in failure_counters:
                failure_counters[hostname] = 0
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
