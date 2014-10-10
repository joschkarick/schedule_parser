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

    def __init__(self):
        pass

    pass


class Docent(object):

    name = ""

    def __init__(self, name=""):
        self.name = name
        pass

    pass


class Room(object):

    def __init__(self):
        pass

    pass