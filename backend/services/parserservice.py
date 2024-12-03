from backend.commons.parser_commons import ParserInput, ParserOutput, ParserSettings
from backend.parsers.base import BaseParser
from ..commons.t2t_logging import log_decorated, log_info

from ..parsers.allennlp import AllennlpParser, ALLENNLP_PARSER_NAME
from ..parsers.flairparser import FlairParser, FLAIR_PARSER_NAME
from ..parsers.spacy import SpacyParser, SPACY_PARSER_NAME

import threading
import time



class ParserService:
    _default_parsers = {}
    _custom_parsers = {}
    _default_paser_loading = {}
    _threads = []
    _parser_settings : ParserSettings = ParserSettings()

    def __init__(self) -> None:
        self._default_paser_loading[ALLENNLP_PARSER_NAME] = lambda : AllennlpParser()
        self._default_paser_loading[FLAIR_PARSER_NAME] = lambda : FlairParser()
        self._default_paser_loading[SPACY_PARSER_NAME] = lambda : SpacyParser()

        self._parser_settings.context_radius = 2

    def load_default_parsers(self) -> None:
        log_decorated(":: Beggining to load parsers")
        parser1 = AllennlpParser()
        log_decorated(":: AllenNLP loaded")
        parser2 = FlairParser()
        log_decorated(":: Flair loaded")
        parser3 = SpacyParser()
        log_decorated(":: Spacy loaded")

        settings: ParserSettings = ParserSettings()
        settings.context_radius = 2

        parser1.settings = settings
        parser2.settings = settings
        parser3.settings = settings

        self._default_parsers[parser1._PARSER_NAME] = parser1
        self._default_parsers[parser2._PARSER_NAME] = parser2
        self._default_parsers[parser3._PARSER_NAME] = parser3

    def get_parser_names(self) -> list[str]:
        return list(self._default_paser_loading.keys())


    def get_parser(self, parser_name: str) -> BaseParser:
        if parser_name not in self._default_parsers:
            log_decorated("LAZY LOADING: " + parser_name)
            self._default_parsers[parser_name] =  self._default_paser_loading[parser_name]()
            self._default_parsers[parser_name].settings = self._parser_settings
            log_decorated("FINISHED LOADING: " + parser_name)

        return self._default_parsers[parser_name]

    def parse_with_selected(self, input: ParserInput, selected_parser: str) -> ParserOutput:
        start_time = time.perf_counter()

        output: ParserOutput =  self.get_parser(selected_parser).accept(input)
        output.elapsed_time = time.perf_counter() - start_time

        log_decorated("Parsing with " + str(output.parser_name) + " took " + str(output.elapsed_time))

        return output


    def confirm_parsers_loaded(self):
        start_time = time.perf_counter()
        outputs: list[ParserOutput] = []
        for parser in self._default_parsers.values():
            outputs.append(parser.accept(ParserInput("The quick brown fox jumped over the lazy brown dog in 1999. Seven seas blow seven windows in text to speech.")))

        for o in outputs:
            print(o)

        log_decorated("PARSER CONFIRMATION COMPLETED IN " + str(time.perf_counter() - start_time))

