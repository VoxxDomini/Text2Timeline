from backend.commons.temporal import TemporalEntity
from backend.parsers.base import BaseParser, ParserOutput, ParserInput
from backend.commons.temporal import TemporalEntity
from typing_extensions import override
from typing import List, Tuple, Dict, Set

class test_plugin_parser(BaseParser):
    def __init__(self):
        pass

    @property
    def settings(self):
        return self.settings

    @settings.setter
    def settings(self, settings):
        self._settings = settings

    @override
    def accept(self, input: ParserInput, contains_no_year_temporals=True, batch_mode=False, batch_offset=-1) -> ParserOutput:
        print("This is a demo plugin, accept will run the parsers on an input and return the ouput")
        return ParserOutput([])

    @override
    def initialize(self) -> None:
        print("This is a demo plugin, initializing it shoud load anything that affects performance if the class requires it")
