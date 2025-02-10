from tkinter import FALSE
from typing import List
from backend.commons.t2t_enums import RendererPaginationSetting
from backend.commons.t2t_logging import log_decorated
from backend.commons.temporal import TemporalEntity
from backend.flask.models.app_templated_models import Render, RenderPlacement, ResultPageModel
from backend.parsers import allennlp
from backend.renderers.extras import events_per_year_bubble_mpl
from backend.services.parserservice import ParserService
from backend.services.renderservice import DEFAULT_RENDERER_MPL, DEFAULT_RENDERER_PLOTLY, RendererService
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

    -- actually, request multithreading is being handled surprisingly well, making parsers stateless should resolve
    most concurrency issues for up to a reasonable amount of users as the file locks don't seem to be causing issues when 
    running the same model on three different texts concurrently
'''

class ResultBuilder():
    def __init__(self, gallery_render_mode: RendererPaginationSetting):
        self.gallery_render_mode = gallery_render_mode
        pass

    def build_no_batching(self, parser_output: ParserOutput, render_service : RendererService) -> ResultPageModel:
        output: ParserOutput = parser_output

        # Trying out dynamic pages for mpl, will render individually
        # render_list = render_service.render_with_all(output)
        render_list = []

        plotly_render : Render = render_service.render_with_selected(DEFAULT_RENDERER_PLOTLY, output)
        plotly_render.placement = RenderPlacement.INTERACTIVE
        render_list.append(plotly_render)

        mpl_renders : List[Render] = []

        if self.gallery_render_mode == RendererPaginationSetting.SINGLE_IMAGE:
            temp_render : Render = render_service.render_with_selected(DEFAULT_RENDERER_MPL, output, render_mode=self.gallery_render_mode)
            temp_render.placement = RenderPlacement.GALLERY
            mpl_renders.append(temp_render)
        elif self.gallery_render_mode == RendererPaginationSetting.PAGES:
            # TODO Expose page size higher up
            split_outputs = self.paginate(output, page_size=15) # TODO calculate this based on output size
            for part in split_outputs:
                temp_render = render_service.render_with_selected(DEFAULT_RENDERER_MPL, part)
                temp_render.placement = RenderPlacement.GALLERY
                mpl_renders.append(temp_render)

        render_list.extend(mpl_renders)
        result_model : ResultPageModel = self.build_from_ouput(output, render_list)
        return self.add_extras(result_model, output)

    # BATCHING DOES NOT SUPPORT DYNAMIC RENDER PAGES YET
    def build_with_batching(self, parser_input, selected_parser, parser_service, render_service, batch_size):
        start_time = time.perf_counter()

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
        return self.add_extras(result_model, output)

    def add_extras(self, result_model: ResultPageModel, parser_output: ParserOutput) -> ResultPageModel:
        render: Render = events_per_year_bubble_mpl(parser_output, group_size=100) # TODO autocalc group size
        render.placement = RenderPlacement.EXTRAS
        result_model.renders.append(render)
        return result_model
    
    def build_from_ouput(self, parser_output: ParserOutput, renders: List[Render]) -> ResultPageModel:
        # TODO hook this pagination control up
        result : ResultPageModel = ResultPageModel(use_pagination=False)
        result.renders = renders
        result.output = parser_output
        return result


    """
    Attempt to make more logical plotly pages for the FE gallery
    this should return a list of outputs, without affecting the original
    containing all temporal entities of the original, where each ouput
    should fit into a single timeline
    """
    def paginate_dynamically(self, output: ParserOutput) -> List[ParserOutput]:
        list : List[ParserOutput] = []

        return list


    # Not the intended usage, being used to test gallery modes on the flask app
    def paginate(self, output: ParserOutput, page_size) -> List[ParserOutput]:
        paginated_content : List[List[TemporalEntity]] = output.get_content_paginated(page_size)
        
        output_pages : List[ParserOutput] = []
        
        for page in paginated_content:
            output_pages.append(ParserOutput(page, finalizeOnInit=False))

        return output_pages
