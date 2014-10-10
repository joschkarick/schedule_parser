#!/usr/bin/python
# -*- coding: latin-1 -*-

__author__ = 'JOSCH'

from event import *
import re
import urllib2
from bs4 import BeautifulSoup


site = "https://basis.uni-bonn.de/qisserver/rds?state=wtree" \
       "&search=1&trex=step&root120142=108307|116100|116093|116108&P.vx=lang"

soup = BeautifulSoup(urllib2.urlopen(site).read())

items = soup.find('td', {"class": "maske"}).find_all('table')

r = re.compile(r'([\s]+)\s')
semester_re = re.compile(r'((WiSe|SoSe) ([0-9]{2,4}(/[0-9]{2})?))\s')
number_re = re.compile(r'([0-9]{9})\s')
event_type_re = re.compile(r'([a-zA-ZöÖäÄüÜ]+[a-zA-ZöÖäÄüÜ ]+)\s')
weekly_hours_re = re.compile(r'([0-9]{1,2}\.[0-9] SWS)\s')
docent_re = re.compile(r'(\s[^;^:]*) ')

events = []
e = Event()
for x in xrange(0, len(items), 2):
    e = Event()
    e.name = items[x].find('h2').find('a').getText()

    # Group all whitespaces
    tmp = r.sub(' ', items[x].find('div', {"class": "klein"}).getText())
    # Reduce all whitespace groups to 1 whitespace
    tmp = ' '.join(tmp.split())

    # Extract each variable via pre-compiled regex
    e.semester = semester_re.search(tmp).group(0)[:-1]
    tmp = tmp[len(e.semester)+1:]

    e.number = number_re.search(tmp).group(0)[:-1]
    tmp = tmp[len(e.number)+1:]

    e.event_type = event_type_re.search(tmp).group(0)[:-1]
    tmp = tmp[len(e.event_type)+1:]

    e.weekly_hours = weekly_hours_re.search(tmp).group(0)[:-1]
    tmp = tmp[len(e.weekly_hours)+1:]

    d = docent_re.findall(tmp)
    for row in d:
        e.docents.append(Docent(row))

    events.append(e)

for event in events:
    print "------------------------------------------------------------------------------------------------------------"
    print event.name
    print event.number
    print event.semester
    print event.weekly_hours
    print event.event_type
    print "Dozenten:"
    for docent in event.docents:
        print "\t", docent.name