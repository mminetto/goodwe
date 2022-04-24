import asyncio
import goodwe
import logging
import sys
import json
from datetime import datetime

#logging.basicConfig(level=logging.DEBUG)

file_cache = 'data.json'
file_control = 'last_exec'
file_error_control = 'error_count'
ip_address = '192.168.1.104'
error_limit = 10
sensor = sys.argv[1]

def timestamp():
    return datetime.strftime(datetime.now(), '%Y%m%d%H%M')

def write_file(file_name, content):
    with open(file_name, "w") as f:
        f.write(content)
        f.close()

def get_content(file_name):
    content = ""
    with open(file_name, "r") as f:
        content = f.readline()
        f.close()

    return content

async def get_data():
    content = get_content(file_control)

    if(int(content) < int(timestamp())):
        try:
            inverter = await goodwe.connect(ip_address, "DT", retries=1)
            runtime_data = await inverter.read_runtime_data()

            with open(file_cache, 'w', encoding='utf-8') as f:
                json.dump(runtime_data, f, indent=4, sort_keys=True, default=str)

            write_file(file_error_control, str(0))

        except:
            count = get_content(file_error_control)
            write_file(file_error_control, str(int(count) + 1))

            if(int(count) > error_limit):
                write_file(file_cache, "{}")

        finally:
            write_file(file_control, timestamp())

    with open(file_cache) as f:
        json_data = json.load(f)
        f.close()

        if sensor in json_data:
            print(json_data[sensor])

asyncio.run(get_data())
