# Network Service Monitor  

A Python script that monitors the availability of network services and sends notifications to Slack when services go down or come back up.

## Features

- Monitors multiple services simultaneously
- Configurable service ports
- Automatic Slack notifications for outages and recoveries
- Failure threshold detection (3 consecutive failures)
- Hourly counter reset
- Continuous monitoring with automatic recovery detection

## Requirements

- Python 3.0 or higher
- Internet connection
- Slack webhook URL (for notifications)

## Configuration

1. Edit the `SERVICES` dictionary in `downDetector.py` to add or modify the services you want to monitor:
```python
SERVICES = {
    "example.com": {"port": 80},
    "another-service.com": {"port": 22}
}
```

2. Configure the monitoring parameters at the top of `downDetector.py`:
```python
# Configuration constants
SLACK_WEBHOOK_URL = "your-slack-webhook-url"
FAILURE_THRESHOLD = 3    # Number of consecutive failures before alerting
CHECK_INTERVAL = 30      # Seconds between service checks
RECOVERY_INTERVAL = 5    # Seconds between recovery checks
CONNECTION_TIMEOUT = 0.2 # Seconds for connection timeout
```

These parameters can be adjusted based on your needs:
- `FAILURE_THRESHOLD`: How many consecutive failures before sending an alert
- `CHECK_INTERVAL`: How often to check each service
- `RECOVERY_INTERVAL`: How often to check for service recovery
- `CONNECTION_TIMEOUT`: How long to wait for a connection response

## Usage

1. Make sure you have Python 3.0 or higher installed
2. Configure the services and Slack webhook URL as described above
3. Run the script:
```bash
python downDetector.py
```

The script will:
- Check each service every 30 seconds
- Send a Slack notification if a service fails 3 times in a row
- Monitor failed services until they recover
- Send a recovery notification when a service comes back up
- Reset failure counters at the start of each hour

### Running as a Systemd Service

To run the script as a systemd service (recommended for production use):

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/network-monitor.service
```

2. Add the following content (adjust paths as needed):
```ini
[Unit]
Description=Network Service Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/script/directory
ExecStart=/usr/bin/python3 /path/to/script/directory/downDetector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable network-monitor
sudo systemctl start network-monitor
```

4. Check the service status:
```bash
sudo systemctl status network-monitor
```

5. View logs:
```bash
journalctl -u network-monitor -f
```

## Monitoring Details

- Connection timeout: 0.2 seconds
- Check interval: 30 seconds
- Failure threshold: 3 consecutive failures
- Recovery check interval: 5 seconds

## Error Handling

The script handles various network conditions:
- Connection timeouts
- Connection failures
- Slack notification failures

All errors are logged to the console for debugging purposes.

## Security Note

For production use, it's recommended to:
1. Move the Slack webhook URL to an environment variable
2. Use a more secure method of storing credentials
3. Consider implementing rate limiting for notifications
