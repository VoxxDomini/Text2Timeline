from backend.commons.parser_commons import ParserInput, ParserOutput
from backend.services.parserservice import ParserService
from backend.commons.t2t_logging import log_info
from typing import List

class ParserComparisonService:
    parser_instances = {}
    parser_ouputs = {}
    
    def __init__(self, parser_service: ParserService):
        self._parser_service = parser_service
        self._raw_input = None
        pass

    def set_raw_input(self, _raw_input: str) -> None:
        self._raw_input = _raw_input

    def load_parsers(self, parser_names: List[str]):
        existing_names = self._parser_service.get_parser_names()

        for parser_name in parser_names:
            if parser_name not in existing_names:
                raise RuntimeError(f"No parser {parser_name} exists")
            else:
                self.parser_instances[parser_name] = self._parser_service.get_parser(parser_name)


    def run_comparisons(self):
        if self._raw_input is None:
            raise RuntimeError(f"No common text to compare parsers has been provided")

        for parser in self.parser_instances.keys():
            # recreating this every time for service interopability
            # just in case state altering methods are used at some point
            parser_input = ParserInput(self._raw_input) 
            output : ParserOutput = self._parser_service.parse_with_selected(parser_input, parser)
            self.parser_ouputs[parser] = output

        
        

        

            

        