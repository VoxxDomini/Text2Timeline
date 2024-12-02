from backend.commons.parser_commons import ParserInput, ParserOutput, ParserSettings
from backend.parsers.base import BaseParser
from ..commons.t2t_logging import log_info

from ..parsers.allennlp import AllennlpParser
from ..parsers.flairparser import FlairParser
from ..parsers.spacy import SpacyParser

import threading
import time


class ParserService:
    _default_parsers = {}
    _custom_parsers = {}

    _threads = []

    def __init__(self) -> None:
        pass

    def init_parsers_async(self) -> None:
        for threadNumber, parser in enumerate(self._default_parsers.values()):
            thread = threading.Thread(target=self.initialize_parser, args=(parser,))
            self._threads.append(thread)
            thread.start()

        for thread in self._threads:
            thread.join()

        log_info("Default parsers finished loading")

    def initialize_parser(self, parser) -> None:
        parser.initialize()
        log_info(f"Thread {threading.get_ident()} - {parser._PARSER_NAME}")

    def load_default_parsers(self) -> None:
        parser1 = AllennlpParser()
        parser2 = FlairParser()
        parser3 = SpacyParser()

        settings: ParserSettings = ParserSettings()
        settings.context_radius = 2

        parser1.settings = settings
        parser2.settings = settings
        parser3.settings = settings

        self._default_parsers[parser1._PARSER_NAME] = parser1
        self._default_parsers[parser2._PARSER_NAME] = parser2
        self._default_parsers[parser3._PARSER_NAME] = parser3

    def get_parser_names(self) -> list[str]:
        return list(self._default_parsers.keys())


    def get_parser(self, parser_name: str) -> BaseParser:
        return self._default_parsers[parser_name]

    def parse_with_selected(self, input: ParserInput, selected_parser: str) -> ParserOutput:
        start_time = time.perf_counter()

        output: ParserOutput =  self._default_parsers[selected_parser].accept(input)
        output.elapsed_time = time.perf_counter() - start_time

        return output


    def confirm_parsers_loaded(self):
        outputs: list[ParserOutput] = []
        for parser in self._default_parsers.values():
            outputs.append(parser.accept(ParserInput("The quick brown fox jumped over the lazy brown dog in 1999. Seven seas blow seven windows in text to speech.")))

        for o in outputs:
            print(o)

