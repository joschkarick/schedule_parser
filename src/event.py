__author__ = 'JOSCH'


class Event(object):

    name = ""
    semester = ""
    event_type = ""
    weekly_hours = 0
    number = 0
    docents = None
    dates = None

    def __init__(self):
        self.docents = []
        self.dates = []
        pass

    pass


class Date(object):

    day = ""
    start_time = ""
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

    def __init__(self, name="", type=""):
        self.name = name
        self.type = type
        pass

    pass


class Room(object):

    def __init__(self):
        pass

    pass