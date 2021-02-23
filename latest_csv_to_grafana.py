import sys

from requests import post
from _datetime import datetime
from pathlib import Path
from extract import get_grafana_credentials

endpoint, api_key = get_grafana_credentials()

interval = 60 * 60

data = []
data_dir = Path.cwd() / 'data'
for csv_file in data_dir.glob('*.csv'):
    lines = csv_file.read_text().splitlines()
    last_line = lines[-1]
    timestamp_text, value_text = last_line.split(',')
    value = float(value_text)
    timestamp = datetime.strptime(timestamp_text, '%Y-%m-%dT%H:%M:%S.%f')
    data.append({'name': f'nibe.{csv_file.stem}',
                 'interval': interval,
                 'value': value,
                 'time': int(timestamp.timestamp())})

if len(data) == 0:
    print(f'No data found in {data_dir} - aborting!')
    sys.exit(-1)

#print(data)

headers = {'Authorization': f'Bearer {api_key}',
           'Content-Type': 'application/json'}
resp = post(endpoint, json=data, headers=headers)
