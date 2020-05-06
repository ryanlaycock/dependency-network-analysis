from datetime import datetime


def log_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
