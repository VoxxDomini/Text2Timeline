from typing import Dict, Union
from backend.commons.parser_commons import ParserInput, ParserOutput
from backend.commons import t2t_logging
from backend.commons.t2t_enums import PluginType, RendererPaginationSetting
from backend.flask.services.result_builder import ResultBuilder
from backend.services.parserservice import ParserService
from backend.services import plugin_service
from backend.services.renderservice import RendererService

'''
Will manage parser service, settings and plugins execution order
'''
class PipelineManagerService:
    
    def __init__(self) -> None: 
        # honestly I might just give up on the singleton parser service, here is a good place to swap it out
        # this is too many workarounds already, loading times will increase though

        self.parser_service = ParserService()

        self._pre_processors = {}
        self._post_processors = {}
        self._gallery_extras = {}

        self.load_plugins()


    def run_pipeline_parser_output(self, parser_input, parser_name) -> ParserOutput:
        if isinstance(parser_input, ParserInput) == False:
            parser_input = ParserInput(parser_input)

        # Pre Processors

        for k in self._pre_processors.keys():
            # TODO add order of operations
            instance = self._pre_processors[k]()
            temp = instance.process(parser_input)
            if isinstance(temp, ParserInput):
                parser_input = temp 

        parser_output = self.parser_service.parse_with_selected(parser_input, parser_name)

        # Post Processors

        for k in self._post_processors.keys():
            # TODO add order of operations
            instance = self._post_processors[k]()
            temp = instance.process(parser_output)
            if isinstance(temp, ParserOutput):
                parser_output = temp

        return parser_output


    def run_pipeline_result_page_model(self, parser_input, parser_name):
        parser_output: ParserOutput = self.run_pipeline_parser_output(parser_input, parser_name)

        result_builder = ResultBuilder(RendererPaginationSetting.PAGES)
        render_service = RendererService()

        result_page = result_builder.build_no_batching(parser_output, render_service)
        return result_page


    def load_plugins(self) -> None:
        t2t_logging.log_info("Beginning to load plugins from pipeline manager")
        
        self.load_and_save_plugin_type(PluginType.PLUGIN_PREPROCESSOR, self._pre_processors)
        self.load_and_save_plugin_type(PluginType.PLUGIN_POSTPROCESSOR, self._post_processors)


    def load_and_save_plugin_type(self, plugin_type: PluginType, storage_map: Dict) -> None:
        plugin_name_class_map = plugin_service.load_plugins(plugin_type)

        for key, value in plugin_name_class_map.items():
            storage_map[key] = lambda : value()

        t2t_logging.log_info(f"Loaded {len(storage_map)} {str(plugin_type.value)} plugins")


    
        
        
    