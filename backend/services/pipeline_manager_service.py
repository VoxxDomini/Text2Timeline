from typing import Union
from backend.commons.parser_commons import ParserInput, ParserOutput
from backend.commons import t2t_logging
from backend.commons.t2t_enums import PluginType
from backend.services.parserservice import ParserService
from backend.services import plugin_service

'''
Will manage parser service, settings and plugins execution order
'''

class PipelineManagerService:
    
    def __init__(self) -> None:
        self.parser_service = ParserService()

        self._pre_processors = {}
        self._post_processors = {}
        self._gallery_extras = {}

        self.load_plugins()


    def run_pipeline_parser_output(self, parser_input, parser_name) -> ParserOutput:
        if isinstance(parser_input, ParserInput) == False:
            parser_input = ParserInput(parser_input)

        # Pre Processors

        parser_output = self.parser_service.parse_with_selected(parser_input, parser_name)

        # Post Processors

        for k in self._post_processors.keys():
            # TODO add order of operations
            instance = self._post_processors[k]()
            temp = instance.process(parser_output)
            if isinstance(temp, ParserOutput):
                parser_output = temp

        return parser_output




    def load_plugins(self) -> None:
        t2t_logging.log_info("Beginning to load plugins from pipeline manager")
        
        # The parser service will load its own plugins
        plugin_name_class_map = plugin_service.load_plugins(PluginType.PLUGIN_POSTPROCESSOR)

        for key, value in plugin_name_class_map.items():
            self._post_processors[key] = lambda : value()

        t2t_logging.log_info(f"Loaded {len(self._post_processors)} post processor plugins")


    
        
        
    