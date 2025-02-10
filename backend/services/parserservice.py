from torch.autograd.grad_mode import F
from backend.commons.parser_commons import ParserInput, ParserOutput, ParserSettings
from backend.commons.t2t_enums import PluginType
from backend.parsers.base import BaseParser
from ..commons.t2t_logging import log_decorated, log_error, log_info

from ..parsers.allennlp import AllennlpParser, ALLENNLP_PARSER_NAME
from ..parsers.flairparser import FlairParser, FLAIR_PARSER_NAME
from ..parsers.spacy import SpacyParser, SPACY_PARSER_NAME
from . import plugin_service

import threading
import time



class ParserService: # Singleton for now
    _custom_parsers = {}
    _default_paser_loading = {}
    _threads = []
    _parser_settings : ParserSettings = ParserSettings()

    _loaded_parsers = {} # only this should have instances, the rest should have lambda class ref

    def __init__(self) -> None:
        self._default_paser_loading[ALLENNLP_PARSER_NAME] = lambda : AllennlpParser()
        self._default_paser_loading[FLAIR_PARSER_NAME] = lambda : FlairParser()
        self._default_paser_loading[SPACY_PARSER_NAME] = lambda : SpacyParser()

        self._parser_settings.context_radius = 2

        self.load_plugin_parsers()

    def load_default_parsers(self) -> None: # maybe should be called pre-load? you can still lazy load by get by name
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

        self._loaded_parsers[parser1._PARSER_NAME] = parser1
        self._loaded_parsers[parser2._PARSER_NAME] = parser2
        self._loaded_parsers[parser3._PARSER_NAME] = parser3


    def load_plugin_parsers(self) -> None:
        # I've changed this to return a map of all plugins found
        # so we can use file name as plugin name and class reference as value
        # so we can have same lazy loading as default plugins
        # why am I saying we?
        plugin_name_class_map = plugin_service.load_plugins(PluginType.PLUGIN_PARSER)

        # Works, should TODO add validation to plugin service
        # that checks that all abstract class methods are implemented
        # cause no IDE errors show up, preferably dynamic
        for key, value in plugin_name_class_map.items():
            self._custom_parsers[key] = lambda : value()
        


    def get_parser_names(self) -> list[str]:
        all_parser_names = []
        if len(self._custom_parsers) > 0:
            all_parser_names.extend(list(self._custom_parsers.keys()))
        all_parser_names.extend(list(self._default_paser_loading.keys()))

        # these are all possible-to-load names, regardless of whether in memory       
        return all_parser_names

    def get_parser(self, parser_name: str) -> BaseParser:
        if parser_name not in self._loaded_parsers:
            log_info(f"{parser_name} not loaded, searching references.")
            parser_class_ref = self.find_parser(parser_name)

            if parser_class_ref is None:
                log_error(f"{parser_name} not found in loaded references, an unprecedented error has occurred. Run.")
                # python 3.9 doesn't support None optional return type, makes you wonder how they released this, let it fail for now
            else:
                log_decorated(f"LAZY LOADING: {parser_name}")
                start_time = time.perf_counter()
                self._loaded_parsers[parser_name] =  parser_class_ref()
                self._loaded_parsers[parser_name].settings = self._parser_settings
                elapsed_time = time.perf_counter() - start_time

                log_decorated(f"FINISHED LOADING: {parser_name} in {str(elapsed_time)}")
        else:
            log_info(f"{parser_name} in memory")

        return self._loaded_parsers[parser_name]


    def find_parser(self, parser_name):
        if parser_name in self._default_paser_loading:
            return self._default_paser_loading[parser_name]

        if parser_name in self._custom_parsers:
            return self._custom_parsers[parser_name]

        return None

    def parse_with_selected(self, input: ParserInput, selected_parser: str) -> ParserOutput:
        start_time = time.perf_counter()

        log_info(f"Beginning to parse")
        output: ParserOutput =  self.get_parser(selected_parser).accept(input)
        output.elapsed_time = time.perf_counter() - start_time
        # currently all default parsers do this, but this more rigid support for plugin parsers
        output.parser_name = selected_parser 

        log_decorated("Parsing with " + str(output.parser_name) + " took " + str(output.elapsed_time))

        return output


    def confirm_parsers_loaded(self):
        start_time = time.perf_counter()
        outputs: list[ParserOutput] = []
        for parser in self._loaded_parsers.values():
            outputs.append(parser.accept(ParserInput("The quick brown fox jumped over the lazy brown dog in 1999. Seven seas blow seven windows in text to speech.")))

        for o in outputs:
            print(o)

        log_decorated("PARSER CONFIRMATION COMPLETED IN " + str(time.perf_counter() - start_time))

    # custom parsers are not expected to implement batching
    # especially since it didn't prove to be much of a performance improvement
    # so we'll just use this to run everything with default settings
    # from wherever this is being called from if it's a custom one
    # maybe add an option later if someone really wants to implement everything
    # TODO add main managing service common for cli/rest and whatever else comes up
    def is_custom_parser(self, parser_namae) -> bool:
        return parser_namae in self._custom_parsers