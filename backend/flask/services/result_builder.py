



from typing import Type, List
from backend.commons.t2t_logging import log_decorated
from backend.flask.models.app_templated_models import Render, ResultPageModel
from backend.parsers import allennlp
from backend.renderers.base_renderer import BaseRenderer
from ...parsers.base import ParserOutput

import time

'''
    Eventually, I would like for only one managing class to expose all
    result-generating services, accepting only parser inputs and a settings file
    and having some processing queues with multiple instances of the parsers, however I've noticed
    that the parsers place locks on the local files of the model, so this would have to be done
    with multiple containers running, and since the current version of the application has multiple models
    for academic purposes, the ram usage would be very high, maybe in a future v2 of the app a more sophisticated
    architecture can be implemented
'''
class ResultBuilder():
    def __init__(self):
        pass

    def build_no_batching(self, parser_input, selected_parser, parser_service, render_service) -> ResultPageModel:
        output: ParserOutput = parser_service.parse_with_selected(parser_input, selected_parser)
        render_list = render_service.render_with_all(output)
        result_model : ResultPageModel = self.build_from_ouput(output, render_list)
        return result_model

    def build_with_batching(self, parser_input, selected_parser, parser_service, render_service, batch_size):
        start_time = time.perf_counter()

        # See which tokenization is better, per batch or total
        if selected_parser == allennlp.ALLENNLP_PARSER_NAME:
            parser_input.tokenize()

        batches = parser_input.get_in_batches_by_percentage(33)
        parser = parser_service.get_parser(selected_parser)

        output: ParserOutput = ParserOutput([], contains_no_year_temporals=True, batch_mode=True)
        last_batch_max_order = 0

        for i, batch in enumerate(batches):
            batch_log_id = str(i) + "/" + str(len(batches))
            log_decorated("Batch " + batch_log_id + " length " + str(len(batch.get_content())))
            new_output = parser.accept(batch, batch_mode=True, batch_offset=last_batch_max_order)
            last_batch_max_order = output._last_batch_max_order
            log_decorated("Batch " + batch_log_id + " new max order " + str(last_batch_max_order))
            output.append_content(new_output)
        
        

        output.finalize()
        output.elapsed_time = time.perf_counter() - start_time

        render_list = render_service.render_with_all(output)
        result_model : ResultPageModel = self.build_from_ouput(output, render_list)
        return result_model
    
    def build_from_ouput(self, parser_output: ParserOutput, renders: List[Render]) -> ResultPageModel:
        result : ResultPageModel = ResultPageModel()
        result.renders = renders
        result.output = parser_output
        return result
