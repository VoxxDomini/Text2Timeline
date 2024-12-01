from typing import Any


class TemporalEntity(object):
    def __init__(self):
        self._event = ""
        self._year = ""
        self._date = ""
        self._context_before = ""
        self._context_after = ""

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, e:str):
        self._event = self.format_string(e)

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, y: str):
        self._year = y

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, d:str):
        self._date = d

    @property
    def context_before(self):
        return self._context_before

    @context_before.setter
    def context_before(self, cb:str):
        self._context_before = self.format_string(cb)

    @property
    def context_after(self):
        return self._context_after

    @context_after.setter
    def context_after(self, ca:str):
        self._context_after = self.format_string(ca)
        

    def format_string(self, s:str) -> str:
        result = s.strip()
        result = result.replace("\n", " ")
        return result

    def __str__(self):
        return str(self._date) + " | " + str(self._year) + " :: " + str(self._event)