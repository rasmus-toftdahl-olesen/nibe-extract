#!/usr/bin/python3

from pathlib import Path
from datetime import datetime
from extract import get_items, get_credentials

username, password = get_credentials()
items = get_items(username, password)

data_dir = Path.cwd() / 'data'
data_dir.mkdir(exist_ok=True)
now = datetime.now().isoformat()

for name, (value, fvalue) in items.items():
    if fvalue is not None:
        fname = name.replace(' ', '_') + '.csv'
        csv_file = data_dir / fname
        with csv_file.open('a') as fp:
            fp.write(f'{now},{fvalue}\n')
