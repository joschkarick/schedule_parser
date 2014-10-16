#!/usr/bin/python
# -*- coding: latin-1 -*-

__author__ = 'JOSCH'

from event import *
import re
import urllib2
from bs4 import BeautifulSoup


def parse_site(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())

    items = soup.find('td', {"class": "maske"}).find_all('table')

    strip_re = re.compile(r'([\s]+)\s')
    semester_re = re.compile(r'((WiSe|SoSe) ([0-9]{2,4}(/[0-9]{2})?))\s')
    number_re = re.compile(r'([0-9]{9})\s')
    event_type_re = re.compile(r'([a-zA-ZöÖäÄüÜ]+[a-zA-ZöÖäÄüÜ ]+)\s')
    weekly_hours_re = re.compile(r'([0-9]{1,2}\.[0-9] SWS)\s')
    docent_re = re.compile(r'(\s[^;^:]*) ')
    date_dates_re = re.compile(r'Termin: |Termine: ')
    day_re = re.compile(r'((Mo|Di|Mi|Do|Fr|Sa|So) ([0-9]{1,2}(:[0-9]{1,2})?) '
                        r'(\([cs]\.t\.\) )?- ([0-9]{1,2}(:[0-9]{1,2})?))|-')


    events = []
    e = Event()
    for x in xrange(0, len(items), 2):
        e = Event()
        e.name = items[x].find('h2').find('a').getText()

        # Group all whitespaces
        tmp = strip_re.sub(' ', items[x].find('div', {"class": "klein"}).getText())
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

        # Parse students
        d = docent_re.findall(tmp)
        for row in d:
            e.docents.append(Docent(row))

        # Parse dates
        date_rows = items[x+1].findAll('tr')
        for date_row in xrange(2, len(date_rows), 3):
            d = Date()
            tmp = strip_re.sub(' ', date_rows[date_row].getText())

            tmp2 = date_dates_re.search(tmp).group(0)
            tmp = tmp[len(tmp2)+1:]

            tmp2 = day_re.search(tmp).groups()
            d.day = tmp2[1]
            d.start_time = tmp2[2]
            d.ct_st = tmp2[4]
            d.end_time = tmp2[5]

            e.dates.append(d)

        events.append(e)

    for event in events:
        print "------------------------------------------------------------------------------------------------------"
        print event.name
        print event.number
        print event.semester
        print event.weekly_hours
        print event.event_type
        print "Dozenten:"
        for docent in event.docents:
            print "\t", docent.name
        print "Dates:"
        for date in event.dates:
            print "\t", date.day, date.start_time, date.ct_st, " - ", date.end_time
    pass

url = "https://basis.uni-bonn.de/qisserver/rds?state=wtree" \
      "&search=1&trex=step&root120142=108307|116100|116093|116108&P.vx=lang"

parse_site(url)