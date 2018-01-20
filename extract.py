#!/usr/bin/python3

import sys
import requests
from bs4 import BeautifulSoup
import socket

if len(sys.argv) < 3:
    print ( 'Usage:' )
    print ( '\t%s [options] <USERNAME> <PASSWORD>' % (sys.argv[0]) )
    print ( 'Options:' )
    print ( '\t--gry <HOSTNAME>\t\tSend a UDP packet with the data to the given Gry host' )
    sys.exit(-1)

GRY_HOST = None
GRY_UDP_PORT = 8124

argv = list(sys.argv)
if '--gry' in argv:
    gryindex = argv.index('--gry')
    GRY_HOST = argv[gryindex + 1]
    del argv[gryindex]
    del argv[gryindex]

USERNAME = argv[1]
PASSWORD = argv[2]

ALLOWED_UNITS = ['%', '°C', 'ºC', 'bar', 'Hz', 'h']

def send_gry ( source_name, value ):
    message = '%s %s' % (source_name, value)
    #print ( message )
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode('utf-8'), (GRY_HOST, GRY_UDP_PORT))
    sock.close()

def is_float(txt):
    try:
        float(txt)
        return True
    except ValueError:
        return False

def is_bool(txt):
    if txt.strip().lower() in ['no', 'yes']:
        return True
    else:
        return False

def to_bool(txt):
    if txt.strip().lower() == 'yes':
        return 1
    else:
        return 0

items = {}
with requests.Session() as s:
    s.get ( 'https://www.nibeuplink.com/Welcome' )
    s.post ( 'https://www.nibeuplink.com/Login', data = {'Email': USERNAME, 'Password': PASSWORD} )
    s.get ( 'https://www.nibeuplink.com/Language/en-GB' )
    for nibeIndex in range(2):
        r = s.get ( 'https://www.nibeuplink.com/System/43106/Status/ServiceInfo/{0}'.format(nibeIndex) )
        open ( 'test.html', 'w' ).write( r.text )

        soup = BeautifulSoup(r.text, 'html.parser')

        for table in soup.find_all('table'):
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) == 2:
                    name = next(tds[0].stripped_strings)
                    value = tds[1].span.text
                    if name not in items:
                        items[name] = value


for key, value in items.items():
    name = 'NIBE.' + key.replace(' ', '_').replace('.', '')
    fvalue = None
    for unit in ALLOWED_UNITS:
        if value.endswith(unit):
            fvalue = float(value[:-(len(unit))])
    if fvalue is None and is_float(value):
        fvalue = float(value)
    if fvalue is None and is_bool(value):
        fvalue = to_bool(value)

    if fvalue is not None:
        if GRY_HOST:
            send_gry ( name, fvalue )
        else:
            print ( name, fvalue )
