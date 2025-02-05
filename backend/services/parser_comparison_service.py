import re
from backend.commons.parser_commons import ParserInput, ParserOutput
from backend.commons.temporal import TemporalEntity
from backend.flask.models.app_templated_models import Render, RenderPlacement, ResultPageModel
from backend.services.parserservice import ParserService
from backend.commons.t2t_logging import log_info
from typing import List

from backend.renderers.extras import parser_comparison_year_vs_no_year_grouped_bar_chart


class HtmlBuilder:
    _content = ""

    def __init__(self):
        pass

    def line(self, text: str):
        self._content = self._content.join(text + "<br>")
        return self

    def build(self):
        return self._content

class ParserComparisonService:
    parser_instances = {}
    parser_outputs :dict[str, ParserOutput] = {}
    
    def __init__(self, parser_service: ParserService):
        self._parser_service = parser_service
        self._raw_input = None
        pass

    def _set_raw_input(self, _raw_input: str) -> None:
        self._raw_input = _raw_input

    def _load_parsers(self, parser_names: List[str]):
        existing_names = self._parser_service.get_parser_names()

        for parser_name in parser_names:
            if parser_name not in existing_names:
                raise RuntimeError(f"No parser {parser_name} exists")
            else:
                self.parser_instances[parser_name] = self._parser_service.get_parser(parser_name)


    def _parse_and_save_outputs(self):
        if self._raw_input is None:
            raise RuntimeError(f"No common text to compare parsers has been provided")

        for parser_name in self.parser_instances.keys():
            # recreating this every time for service interopability
            # just in case state altering methods are used at some point
            self._parser_input = ParserInput(self._raw_input) 
            output : ParserOutput = self._parser_service.parse_with_selected(self._parser_input, parser_name)
            self.parser_outputs[parser_name] = output


    def parse_and_compare(self, parser_names: List[str], common_input: str):
        self._set_raw_input(common_input)
        self._load_parsers(parser_names)
        self._parse_and_save_outputs()


    def calculate_average_event_length(self, parser_output: ParserOutput):
        total_length = 0
        total_count = 0

        entities: List[TemporalEntity] = parser_output.content

        for entity in entities:
            total_length += len(entity.event)
            total_count += 1

        return total_length / total_count


    def build_result_page_model(self) -> ResultPageModel:
        result_page = ResultPageModel(use_pagination=False)
        p_outputs = list(self.parser_outputs.values())
        
        # ADD all additional renders for every statistic here, everything should sort itself out autmatically

        render: Render = parser_comparison_year_vs_no_year_grouped_bar_chart(p_outputs)
        render.placement = RenderPlacement.EXTRAS

        result_page.renders.append(render)
        result_page.flavor_text = self.generate_common_input_description()
        return result_page

    def generate_common_input_description(self) -> str:
        html_builder = HtmlBuilder()
    
        # just realized builders are super ugly in python :(
        html_builder.line(f"Comparing {list(self.parser_outputs.keys())} on a document of length {len(self._parser_input._content)}")


        return html_builder.build()




        

        

            

        