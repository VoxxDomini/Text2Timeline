from typing import Dict, Union
from backend.commons.parser_commons import ParserInput, ParserOutput
from backend.commons import t2t_logging
from backend.commons.t2t_enums import PluginType, RendererPaginationSetting
from backend.flask.models.app_templated_models import PluginInformationModel, Render, RenderPlacement, ResultPageModel
from backend.flask.services.result_builder import ResultBuilder
from backend.services.parserservice import ParserService
from backend.services import plugin_service
from backend.services.renderservice import RendererService

'''
Will manage parser service, settings and plugins execution order
'''

PROCESSOR_EXECUTION_ORDER_FIELD_NAME = "processor_order"

class PipelineManagerService:
    
    def __init__(self) -> None: 
        # honestly I might just give up on the singleton parser service, here is a good place to swap it out
        # this is too many workarounds already, loading times will increase though

        self.parser_service = ParserService()

        self._pre_processors = {}
        self._post_processors = {}
        self._gallery_extras = {} # pipeline manager is currently a singleton, keep in mind :)
        self._disabled_keys = []

        self.load_plugins()


    def run_pipeline_parser_output(self, parser_input, parser_name) -> ParserOutput:
        if isinstance(parser_input, ParserInput) == False:
            parser_input = ParserInput(parser_input)

        # Pre Processors
        pre_processors = self.build_processor_execution_order_list(self._pre_processors)
        for pp in pre_processors:
            temp = pp.process(parser_input)

            if isinstance(temp, ParserInput):
                parser_input = temp

        parser_output = self.parser_service.parse_with_selected(parser_input, parser_name)

        # Post Processors

        post_processors = self.build_processor_execution_order_list(self._post_processors)
        for pp in post_processors:
            temp = pp.process(parser_output)

            if isinstance(temp, ParserOutput):
                parser_output = temp

        return parser_output


    def run_pipeline_result_page_model(self, parser_input, parser_name):
        parser_output: ParserOutput = self.run_pipeline_parser_output(parser_input, parser_name)

        result_builder = ResultBuilder(RendererPaginationSetting.PAGES)
        render_service = RendererService()

        result_page: ResultPageModel = result_builder.build_no_batching(parser_output, render_service)
        
        self.append_plugin_gallery_extras(result_page)
        return result_page


    def append_plugin_gallery_extras(self, result_page: ResultPageModel):
        for k in self._gallery_extras:
            if k in self._disabled_keys:
                continue

            new_render: Render = self._gallery_extras[k](result_page.output)
            new_render.placement = RenderPlacement.EXTRAS
            result_page.renders.append(new_render)


    def load_plugins(self) -> None:
        t2t_logging.log_info("Beginning to load plugins from pipeline manager")
        
        self.load_and_save_plugin_type(PluginType.PLUGIN_PREPROCESSOR, self._pre_processors)
        self.load_and_save_plugin_type(PluginType.PLUGIN_POSTPROCESSOR, self._post_processors)
        self.load_and_save_plugin_type(PluginType.PLUGIN_GALLERYEXTRA, self._gallery_extras)


    def load_and_save_plugin_type(self, plugin_type: PluginType, storage_map: Dict) -> None:
        plugin_name_class_map = plugin_service.load_plugins(plugin_type)

        for key, value in plugin_name_class_map.items():
            storage_map[key] = value()
            t2t_logging.log_info(f"Loaded {key}")

        t2t_logging.log_info(f"Loaded {len(storage_map)} {str(plugin_type.value)} plugins")


    def build_processor_execution_order_list(self, processor_storage_map: Dict):
        ordered_processors = []
        unordered_processors = []

        for k in processor_storage_map:
            if k in self._disabled_keys: #i'd like this to be more generic but kinda tired TODO
                continue

            instance = processor_storage_map[k]
            if self.get_processor_order_if_present(instance):
                ordered_processors.append(instance)
            else:
                unordered_processors.append(instance)

        ordered_processors = sorted(ordered_processors, key=lambda x: getattr(x, PROCESSOR_EXECUTION_ORDER_FIELD_NAME))
        ordered_processors.extend(unordered_processors)

        return ordered_processors

    def get_processor_order_if_present(self, processor_instance):
        try:
            return getattr(processor_instance, PROCESSOR_EXECUTION_ORDER_FIELD_NAME)
        except:
            return None

    
        
        
def get_plugin_information_model(pipeline_manager: PipelineManagerService):
    plugin_info = PluginInformationModel()

    plugin_info.parsers = list(pipeline_manager.parser_service._custom_parsers.keys())
    plugin_info.gallery_extras = list(pipeline_manager._gallery_extras.keys())
    plugin_info.post_processors = list(pipeline_manager._post_processors.keys())
    plugin_info.pre_processors = list(pipeline_manager._pre_processors.keys())

    return plugin_info