



from typing import Type, List
from backend.flask.models.app_templated_models import Render, ResultPageModel
from backend.renderers.base_renderer import BaseRenderer
from ...parsers.base import ParserOutput

class ResultBuilder():
    def __init__(self):
        pass

    # intially testing with single renderer
    # should eventually support all possible outputs into a single
    # result page
    def build(self, parser_output: ParserOutput, renders: List[Render]) -> ResultPageModel:
        result : ResultPageModel = ResultPageModel()
        result.renders = renders
        result.output = parser_output
        return result
