__author__ = 'Joschka Rick'


from enum_wrapper import DeclEnum
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Time, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


event_person_association = Table('event_person_association', Base.metadata,
                                 Column('event_id', Integer, ForeignKey('event.id')),
                                 Column('person_id', Integer, ForeignKey('person.id')))

date_person_association = Table('date_person_association', Base.metadata,
                                Column('date_id', Integer, ForeignKey('date.id')),
                                Column('person_id', Integer, ForeignKey('person.id')))

event_date_association = Table('event_date_association', Base.metadata,
                               Column('event_id', Integer, ForeignKey('event.id')),
                               Column('date_id', Integer, ForeignKey('date.id')))


class Day(DeclEnum):
    monday = "Mo", "Montag"
    tuesday = "Di", "Dienstag"
    wednesday = "Mi", "Mittwoch"
    thursday = "Do", "Donnerstag"
    friday = "Fr", "Freitag"
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

    docents = relationship('Person',
                           secondary=event_person_association,
                           backref='events')

    dates = relationship('Date',
                         secondary=event_date_association)

    def __init__(self):
        pass

    pass


class Date(Base):
    __tablename__ = 'date'

    id = Column(Integer, primary_key=True)
    day = Column(Day.db_type(), nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    ct_st = Column(String(10), nullable=True)
    repetition = Column(String(10), nullable=True)
    room = Column(String(50), nullable=True)
    info = Column(String(250), nullable=True)

    teachers = relationship('Person',
                            secondary=date_person_association)

    def __init__(self):
        self.teachers = []
        pass

    pass


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True, nullable=False)
    basis_pid = Column(Integer, nullable=False)
    last_name = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    sex = Column(String(10), nullable=True)
    academic_degree = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)

    def __init__(self):
        pass

    pass


def initiate_db():
    engine = create_engine('sqlite:///event_test.sqlite')
    Base.metadata.create_all(engine)
    return engine