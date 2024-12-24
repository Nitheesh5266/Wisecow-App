#!/usr/bin/env python3
import requests
import time
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    filename='app_health.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HealthChecker:
    def __init__(self, endpoints):
        self.endpoints = endpoints
        self.status_history = {}

    def check_endpoint(self, url):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            status = {
                'status_code': response.status_code,
                'response_time': response_time,
                'is_up': 200 <= response.status_code < 400,
                'timestamp': datetime.now().isoformat()
            }

            # Update history
            if url not in self.status_history:
                self.status_history[url] = []
            self.status_history[url].append(status)

            # Keep only last 100 checks
            if len(self.status_history[url]) > 100:
                self.status_history[url].pop(0)

            return status

        except requests.RequestException as e:
            error_status = {
                'status_code': None,
                'response_time': None,
                'is_up': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            if url not in self.status_history:
                self.status_history[url] = []
            self.status_history[url].append(error_status)
            
            return error_status

    def generate_report(self):
        report = {
            'timestamp': datetime.now().isoformat(),
            'endpoints': {}
        }

        for url in self.endpoints:
            history = self.status_history.get(url, [])
            if history:
                latest = history[-1]
                uptime = sum(1 for check in history if check['is_up']) / len(history) * 100
                avg_response_time = sum(
                    check['response_time'] 
                    for check in history 
                    if check['response_time'] is not None
                ) / len([check for check in history if check['response_time'] is not None])

                report['endpoints'][url] = {
                    'current_status': 'UP' if latest['is_up'] else 'DOWN',
                    'uptime_percentage': uptime,
                    'average_response_time': avg_response_time,
                    'latest_check': latest
                }

        return report

def main():
    # Configure your endpoints here
    endpoints = [
        'http://localhost:8080/health',
        'http://localhost:8080/api'
    ]

    checker = HealthChecker(endpoints)

    while True:
        try:
            for url in endpoints:
                status = checker.check_endpoint(url)
                if not status['is_up']:
                    logging.warning(f'Endpoint {url} is DOWN: {status}')
                else:
                    logging.info(f'Endpoint {url} is UP: {status}')

            # Generate and save report
            report = checker.generate_report()
            with open('health_report.json', 'w') as f:
                json.dump(report, f, indent=2)

            time.sleep(60)  # Check every minute

        except Exception as e:
            logging.error(f'Health check error: {str(e)}')
            time.sleep(60)

if __name__ == '__main__':
    main()