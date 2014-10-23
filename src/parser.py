#!/usr/bin/python
# -*- coding: latin-1 -*-

__author__ = 'Joschka Rick'

from event import *
import datetime
import re
import urllib2
from bs4 import BeautifulSoup
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


strip_re = re.compile(r'([\s]+)\s')
semester_re = re.compile(r'((WiSe|SoSe) ([0-9]{2,4}(/[0-9]{2})?))\s')
number_re = re.compile(r'([0-9]{1,9}|\(Keine\sNummer\))\s')
event_type_re = re.compile(r'([a-zA-ZöÖäÄüÜ]+[a-zA-ZöÖäÄüÜ ]+)\s?')
weekly_hours_re = re.compile(r'([0-9]{1,2}\.[0-9] SWS)\s')
person_re = re.compile(r'(\s[^;^:]*) ')
day_re = re.compile(r'((([0-9]{1,2})(:([0-9]{1,2}))?|-) (\([cs]\.t\.\))? ?- (([0-9]{1,2})(:([0-9]{1,2}))?|-)|-)'
                    r' ?(wöch|woch|Block|täglich|Einzel)?')
date_span_re = re.compile(r'(\d{2}\.\d{2}\.\d{4}|-) ?(bis|-) ?(\d{2}\.\d{2}\.\d{4}|-)')

visited_sites = []

engine = initiate_db()

DBSession = sessionmaker(bind=engine)
session = DBSession()

PARSE_SUBPAGES = False


def parse_site(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())

    subpages = soup.find_all('a', {"class": "ueb", "title": re.compile(r'.* öffnen')})

    if PARSE_SUBPAGES:
        for subpage in subpages:
            subpage_url = subpage['href']
            page_title = subpage['title']
            if not subpage_url in visited_sites:
                visited_sites.append(subpage_url)
                #parse_site(subpage_url)

    tmp = soup.find('td', {"class": "maske"})
    if not tmp:
        return

    items = tmp.find_all('table')
    if not items:
        return

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

        result = weekly_hours_re.search(tmp)
        if result:
            e.weekly_hours = result.group(0)[:-1]
            tmp = tmp[len(e.weekly_hours)+1:]
        else:
            e.weekly_hours = None

        # Parse docents
        d = person_re.findall(tmp)
        for row in d:
            e.docents.append(Person(row, "docent"))

        # Parse each date
        date_rows = items[x+1].find_all('tr')
        for date_row in xrange(2, len(date_rows), 3):
            d = Date()

            # Get all columns from the event date
            entries = date_rows[date_row].find_all('td', {"colspan": False})
            if len(entries) != 7:
                continue

            # Parse each cell
            tmp = strip_re.sub(' ', entries[1].getText().replace(u'\xa0', ' '))
            d.day = Day.from_string("Do")

            tmp = strip_re.sub(' ', entries[2].getText().replace(u'\xa0', ' '))
            tmp = day_re.search(tmp.strip())
            if tmp.group(3) and tmp.group(5):
                d.start_time = datetime.time(hour=int(tmp.group(3)), minute=int(tmp.group(5)))
            else:
                d.start_time = datetime.time()

            d.end_time = tmp.group(5)
            d.ct_st = tmp.group(4)
            d.repetition = tmp.group(7)

            tmp = strip_re.sub(' ', entries[3].getText().replace(u'\xa0', ' '))
            d.room = tmp.strip()

            tmp = strip_re.sub(' ', entries[4].getText().replace(u'\xa0', ' '))
            t = person_re.findall(tmp)
            for row in t:
                d.teachers.append(Person(row, "teacher"))

            tmp = strip_re.sub(' ', entries[5].getText().replace(u'\xa0', ' '))
            d.info = tmp[1:]

            tmp = strip_re.sub(' ', entries[6].getText().replace(u'\xa0', ' '))
            tmp = date_span_re.search(tmp)
            if tmp:
                d.start_date = tmp.group(1)
                d.end_date = tmp.group(3)

            e.dates.append(d)

        session.add_all(e.dates)
        events.append(e)

    #session.add_all(events)
    session.commit()

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
        if len(e.dates) > 0:
            print "Dates:"
            for date in event.dates:
                print "\t", date.day
                print "\t\t", date.start_time, date.ct_st, "-", date.end_time, date.repetition
                print "\t\t", date.start_date, "-", date.end_date
                print "\t\t", date.info
                if len(date.teachers) > 0:
                    print "\t\t", "Teachers:"
                    for teacher in date.teachers:
                        print "\t\t\t", teacher.name
    pass

main = "https://basis.uni-bonn.de/qisserver/rds;jsessionid=7C21B64E2DD0ADAE6A8A267B99FC718D" \
       "?state=wtree&search=1&trex=step&root120142=108307&P.vx=lang"

site1 = "https://basis.uni-bonn.de/qisserver/rds" \
        "?state=wtree&search=1&trex=step&root120142=108307|116100|116093|116108&P.vx=lang"

parse_site(site1)

