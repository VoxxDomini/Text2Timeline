from backend.commons.parser_commons import ParserSettings
from backend.commons.temporal import TemporalEntity
from backend.parsers.base import BaseParser, ParserOutput, ParserInput
from backend.commons.temporal import TemporalEntity
from typing_extensions import override
from typing import List, Tuple, Dict, Set

class test_plugin_parser(BaseParser):
    def __init__(self):
        pass

    '''
        Parser settings include context radius .etc
        Not supporting them will remove compatibility with customizability elements
        But main part of the system's output will not be affected
    '''
    @property
    def settings(self):
        return self.settings

    @settings.setter
    def settings(self, settings: ParserSettings):
        self._settings = settings

    '''
        contains_no_year_temporals - indicates whether this parser will be handling unspecified temporal events e.g. "Tomorrow, i'll wash the dishes"
            make sure to expose this as self.contains_no_year_temporals or self._contains_no_year_temporals to let the system know expected behavior

        batch_mode - keep this at false, while the built-in parsers support batching, there were no discernable performance improvements
    '''
    @override
    def accept(self, input: ParserInput, contains_no_year_temporals=True, batch_mode=False, batch_offset=-1) -> ParserOutput:
        '''
            Accepts an unmodified ParserInput wrapper of the raw text.
            Expects at minimum a list of Temporal entities and whether you've included no_year
        '''
        return ParserOutput([])

    @override
    def initialize(self) -> None:
        '''
            Use this method to load/import anything that will need a bit of time to load so it can be decouple from instanciation
        '''
        raise NotImplementedError
