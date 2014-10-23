__author__ = 'Joschka Rick'


from enum_wrapper import DeclEnum
from sqlalchemy import Enum
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Day(DeclEnum):
    montag = "Mo", "Montag"
    dienstag = "Di", "Dienstag"
    mittwoch = "Mi", "Mittwoch"
    donnerstag = "Do", "Donnerstag"
    freitag = "Fr", "Freitag"
    samstag = "Sa", "Samstag"
    sonntag = "So", "Sonntag"
    unknown = "-", "Unknown"


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    semester = Column(String(10), nullable=True)
    number = Column(Integer, nullable=True)
    event_type = Column(String(100), nullable=True)
    weekly_hours = Column(Integer, nullable=True)

    docents = None
    dates = None

    def __init__(self):
        self.docents = []
        self.dates = []
        pass

    pass


class Date(Base):
    __tablename__ = 'event_date'

    id = Column(Integer, primary_key=True)
    #day = Column(Enum("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So", name='day_enum'), nullable=True)
    day = Column(Day.db_type(), nullable=True)
    start_time = Column(Time, nullable=True)

    end_time = ""
    start_date = ""
    end_date = ""
    ct_st = ""
    repetition = ""
    room = ""
    teachers = None
    info = ""

    def __init__(self):
        self.teachers = []
        pass

    pass


class Person(object):

    name = ""
    type = ""

    def __init__(self, name="", role=""):
        self.name = name
        self.type = role
        pass

    pass


class Room(object):

    def __init__(self):
        pass

    pass


def initiate_db():
    engine = create_engine('sqlite:///event_test.sqlite')
    Base.metadata.create_all(engine)
    return engine