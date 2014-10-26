#!/usr/bin/python
# -*- coding: latin-1 -*-

__author__ = 'Joschka Rick'

from event import *
import datetime
import re
import urllib2
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker


strip_re = re.compile(r'([\s]+)\s')
semester_re = re.compile(r'((WiSe|SoSe) ([0-9]{2,4}(/[0-9]{2})?))\s')
number_re = re.compile(r'([0-9]{1,9}|\(Keine\sNummer\))\s')
event_type_re = re.compile(r'([a-zA-Z������]+[a-zA-Z������ ]+)\s?')
weekly_hours_re = re.compile(r'([0-9]{1,2}\.[0-9] SWS)\s')
person_re = re.compile(r'(\s[^;^:]*)\s')
time_re = re.compile(r'(((([0-9]{1,2})(:([0-9]{1,2}))?) ?(\([cs]\.t\.\))? - (([0-9]{1,2})(:([0-9]{1,2}))?))|-)'
                     r' ?(w�ch|woch|Block|t�glich|Einzel|-)')
date_span_re = re.compile(r'((\d{2})\.(\d{2})\.(\d{4})|-) ?(bis|-) ?((\d{2})\.(\d{2})\.(\d{4})|-)')
pid_re = re.compile(r'&personal\.pid=([0-9]+)')

visited_sites = []
scanned_basis_pids = []
persons = []

engine = initiate_db()

DBSession = sessionmaker(bind=engine)
session = DBSession()

PARSE_SUBPAGES = False


def parse_person(url):
    # Get basis id from persons href
    basis_pid = pid_re.search(url).group(1)

    # If there is no PID, skip the person
    if not basis_pid:
        return

    # If the person was already parsed, skip
    if basis_pid in scanned_basis_pids:
        return filter(lambda person: person.basis_pid == basis_pid, persons)[0]

    soup = BeautifulSoup(urllib2.urlopen(url).read())

    p = Person()
    p.basis_pid = basis_pid
    p.last_name = strip_re.sub(' ', soup.find('td', {'headers': 'basic_1'}).getText()).strip()
    p.sex = strip_re.sub(' ', soup.find('td', {'headers': 'basic_2'}).getText()).strip()
    p.first_name = strip_re.sub(' ', soup.find('td', {'headers': 'basic_3'}).getText()).strip()
    p.academic_degree = strip_re.sub(' ', soup.find('td', {'headers': 'basic_9'}).getText()).strip()
    p.status = strip_re.sub(' ', soup.find('td', {'headers': 'basic_10'}).getText()).strip()

    session.add(p)
    scanned_basis_pids.append(basis_pid)
    persons.append(p)

    return p


def parse_event_list(url):
    pass


def parse_site(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())

    subpages = soup.find_all('a', {"class": "ueb", "title": re.compile(r'.* �ffnen')})

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
        parent_div = items[x].find('div', {"class": "klein"})
        tmp = strip_re.sub(' ', parent_div.getText())
        # Reduce all whitespace groups to 1 whitespace
        tmp = ' '.join(tmp.split())

        # Extract each variable via pre-compiled regex
        # Semester
        e.semester = semester_re.search(tmp).group(0)[:-1]
        tmp = tmp[len(e.semester)+1:]

        # Course number
        e.number = number_re.search(tmp).group(0)[:-1]
        tmp = tmp[len(e.number)+1:]

        # Course type
        e.event_type = event_type_re.search(tmp).group(0)[:-1]
        tmp = tmp[len(e.event_type)+1:]

        # Weekly effort in hours
        result = weekly_hours_re.search(tmp)
        if result:
            e.weekly_hours = result.group(0)[:-1]
            tmp = tmp[len(e.weekly_hours)+1:]
        else:
            e.weekly_hours = None

        # Docents
        d = parent_div.find_all('a', {'title': re.compile(r'Mehr Informationen zu (.*)')})
        for docent in d:
            p = parse_person(docent['href'])
            if p:
                e.docents.append(p)

        # Parse each date
        date_rows = items[x+1].find_all('tr')
        for date_row in xrange(2, len(date_rows), 3):

            # Get all columns from the event date
            entries = date_rows[date_row].find_all('td', {"colspan": False})
            if len(entries) != 7:
                continue

            d = Date()

            # Parse each cell
            # Day of the date
            tmp = strip_re.sub(' ', entries[1].getText().replace(u'\xa0', ' '))
            d.day = Day.from_string(tmp.strip())

            # Time
            tmp = strip_re.sub(' ', entries[2].getText().replace(u'\xa0', ' '))
            tmp = time_re.search(tmp.strip())

            hour = int(tmp.group(4)) if tmp.group(4) else 0
            minute = int(tmp.group(6)) if tmp.group(6) else 0
            d.start_time = datetime.time(hour=hour, minute=minute)

            hour = int(tmp.group(9)) if tmp.group(9) else 0
            minute = int(tmp.group(11)) if tmp.group(11) else 0
            d.end_time = datetime.time(hour=hour, minute=minute)

            d.ct_st = tmp.group(7)
            d.repetition = tmp.group(12)

            # Room
            tmp = strip_re.sub(' ', entries[3].getText().replace(u'\xa0', ' '))
            d.room = tmp.strip()

            # Persons
            teachers = entries[4].find_all('a', {'title': re.compile(r'Mehr Informationen zu (.*)')})
            for teacher in teachers:
                t = parse_person(teacher['href'])
                if t:
                    d.teachers.append(t)

            # Comments/Info
            tmp = strip_re.sub(' ', entries[5].getText().replace(u'\xa0', ' '))
            d.info = tmp[1:]

            # Start and end date
            tmp = strip_re.sub(' ', entries[6].getText().replace(u'\xa0', ' '))
            tmp = date_span_re.search(tmp)
            if tmp and tmp.group(1):
                d.start_date = datetime.date(day=int(tmp.group(2)), month=int(tmp.group(3)), year=int(tmp.group(4)))
            if tmp and tmp.group(6):
                d.end_date = datetime.date(day=int(tmp.group(7)), month=int(tmp.group(8)), year=int(tmp.group(9)))

            e.dates.append(d)

        session.add_all(e.dates)
        events.append(e)

    session.add_all(events)
    session.commit()

    for event in events:
        print "------------------------------------------------------------------------------------------------------"
        print event.name
        print event.number
        print event.semester
        print event.weekly_hours
        print event.event_type
        print "Dozenten:"
        for person in event.docents:
            print "\t", person.academic_degree, person, person.first_name, person.last_name
        if len(e.dates) > 0:
            print "Dates:"
            for date in event.dates:
                print "\t", date.day
                print "\t\t", date.start_time, date.ct_st, "-", date.end_time, date.repetition
                print "\t\t", date.start_date, "-", date.end_date
                print "\t\t", date.info
                if len(date.teachers) > 0:
                    print "\t\t", "Teachers:"
                    for person in date.teachers:
                        print "\t\t\t", person.academic_degree, person.first_name, person.last_name
    pass

main = "https://basis.uni-bonn.de/qisserver/rds;jsessionid=7C21B64E2DD0ADAE6A8A267B99FC718D" \
       "?state=wtree&search=1&trex=step&root120142=108307&P.vx=lang"

site1 = "https://basis.uni-bonn.de/qisserver/rds" \
        "?state=wtree&search=1&trex=step&root120142=108307|116100|116093|116108&P.vx=lang"

parse_site(site1)

#person1 = "https://basis.uni-bonn.de/qisserver/rds?state=verpublish&status=init&vmfile=no&moduleCall=webInfo" \
#          "&publishConfFile=webInfoPerson&publishSubDir=personal&keep=y&purge=y&personal.pid=1323"

#parse_person(person1)
