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
        print("ACCEPT METHOD CALLED FROM PLUGIN")
        return ParserOutput([])

    @override
    def initialize(self) -> None:
        print("I'm an idiot")
