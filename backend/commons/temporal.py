from enum import Enum
from typing import Any


class TemporalEntityType(Enum):
    WITH_YEAR = 1,
    NO_YEAR = 2

class TemporalEntity(object):
    def __init__(self):
        self._order : int = -1
        self._entity_type : TemporalEntityType = TemporalEntityType.WITH_YEAR
        self._event = ""
        self._year = ""
        self._date = ""
        self._context_before = ""
        self._context_after = ""

        # Experimental, to be used for NO_YEAR types in an attempt to gather more context
        self._year_before = ""
        self._year_after = ""

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
    def entity_type(self):
        return self._entity_type

    @entity_type.setter
    def entity_type(self, entity_type: TemporalEntityType):
        self._entity_type = entity_type

    @property
    def order(self) -> int:
        return self._order

    @order.setter
    def order(self, order: int):
        self._order = order

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
        if self.entity_type == TemporalEntityType.WITH_YEAR:
            return str(self._date) + " | " + str(self._year) + " :: " + str(self._event)
        elif self.entity_type == TemporalEntityType.NO_YEAR:
            return str(self._order) + " | " + str(self._year_before) + "|" + self.date + " :: (" + self.context_before + ") " + str(self._event)
        else:
            return "MISSING IMPLEMENTATION FOR " + str(self.entity_type)