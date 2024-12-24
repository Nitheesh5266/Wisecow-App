#!/usr/bin/env python3
import psutil
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='system_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Thresholds
THRESHOLDS = {
    'cpu_percent': 80.0,
    'memory_percent': 80.0,
    'disk_percent': 90.0
}

def check_cpu():
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > THRESHOLDS['cpu_percent']:
        logging.warning(f'High CPU usage: {cpu_percent}%')
    return cpu_percent

def check_memory():
    memory = psutil.virtual_memory()
    if memory.percent > THRESHOLDS['memory_percent']:
        logging.warning(f'High memory usage: {memory.percent}%')
    return memory.percent

def check_disk():
    disk = psutil.disk_usage('/')
    if disk.percent > THRESHOLDS['disk_percent']:
        logging.warning(f'High disk usage: {disk.percent}%')
    return disk.percent

def check_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            if pinfo['cpu_percent'] > 50 or pinfo['memory_percent'] > 50:
                processes.append(pinfo)
                logging.warning(f'High resource process: {pinfo}')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes

def main():
    while True:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cpu_usage = check_cpu()
            memory_usage = check_memory()
            disk_usage = check_disk()
            high_resource_processes = check_processes()

            logging.info(f"""
System Status at {timestamp}:
CPU Usage: {cpu_usage}%
Memory Usage: {memory_usage}%
Disk Usage: {disk_usage}%
""")

            time.sleep(60)  # Check every minute

        except Exception as e:
            logging.error(f'Monitoring error: {str(e)}')
            time.sleep(60)

if __name__ == '__main__':
    main()