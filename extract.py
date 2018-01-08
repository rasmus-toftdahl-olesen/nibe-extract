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

ALLOWED_UNITS = ['%', '°C', 'ºC']

def send_gry ( source_name, value ):
    message = '%s %s' % (source_name, value)
    #print ( message )
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode('utf-8'), (GRY_HOST, GRY_UDP_PORT))
    sock.close()

items = []
with requests.Session() as s:
    s.get ( 'https://www.nibeuplink.com/Welcome' )
    s.post ( 'https://www.nibeuplink.com/Login', data = {'Email': USERNAME, 'Password': PASSWORD} )
    s.get ( 'https://www.nibeuplink.com/Language/en-GB' )
    r = s.get ( 'https://www.nibeuplink.com/System/43106/Status/ServiceInfo/0' )
    open ( 'test.html', 'w' ).write( r.text )

    soup = BeautifulSoup(r.text, 'html.parser')

    for table in soup.find_all('table'):
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 2:
                items.append ( (next(tds[0].stripped_strings), tds[1].span.text) )

for key, value in items:
    for unit in ALLOWED_UNITS:
        if value.endswith(unit):
            name = 'NIBE.' + key.replace(' ', '_').replace('.', '')
            fvalue = float(value[:-(len(unit))])
            if GRY_HOST:
                send_gry ( name, fvalue )
            else:
                print ( name, fvalue )
