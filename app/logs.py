from datetime import datetime
import os
def log_operation(message):
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    now = datetime.now()
    time = now.strftime(timestamp_format)
    FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/logs.txt')
    with open(FILE_PATH, 'a') as file:
        file.write( time +":"+ message )
        file.write('\n')
