from io import BytesIO
import re

from typing import List, Callable, Type
from backend.commons.parser_commons import ParserInput, ParserOutput, ParserSettings
from backend.commons.t2t_enums import DEFAULT_RENDERER_MPL, DEFAULT_RENDERER_PLOTLY, RendererPaginationSetting
from backend.flask.models.app_templated_models import Render
from backend.renderers.base_renderer import BaseRenderer, RendererOutputType, RendererSettings
from backend.renderers.mpl import MPLRenderer
from backend.renderers.plotly import PlotlyRenderer

from ..commons.t2t_logging import log_info

import base64

class RendererService():
    renderers = {}

    def __init__(self) -> None:
        self.renderers[DEFAULT_RENDERER_MPL] = lambda : self.create_mpl_renderer()
        self.renderers[DEFAULT_RENDERER_PLOTLY] = lambda : self.create_plotly_renderer()

    def create_plotly_renderer(self) -> PlotlyRenderer:
        renderer = PlotlyRenderer()
        renderer.output_type = RendererOutputType.EMBEDDED
        renderer.settings = self.create_renderer_settings(renderer._RENDERER_NAME)
        return renderer

    def create_mpl_renderer(self) -> MPLRenderer:
        renderer = MPLRenderer()
        renderer.output_type = RendererOutputType.EXPORT_IMAGE_BYTES
        renderer.settings = self.create_renderer_settings(renderer._RENDERER_NAME)
        return renderer
    
    def create_renderer_settings(self, renderer_name: str) -> RendererSettings:
        return RendererSettings()

    def get_renderer(self, renderer_name: str) -> BaseRenderer:
        if renderer_name not in self.renderers:
            raise ValueError("Renderer name ", renderer_name, " not recognized")

        return self.renderers[renderer_name]()

    def get_renderer_names(self) -> List[str]:
        return list(self.renderers.keys())

    def render_with_selected(self, renderer_selection: str, parser_output : ParserOutput, render_mode=RendererPaginationSetting.PAGES) -> Render:
        renderer : BaseRenderer = self.get_renderer(renderer_selection)
        renderer.accept(parser_output, render_mode)
        output = self.handle_output(renderer)
        return output

    def render_with_all(self, parser_output: ParserOutput) -> List[Render]:
        renders: List[Render] = []
        for renderer_name in self.get_renderer_names():
            instance = self.get_renderer(renderer_name)
            instance.accept(parser_output)
            renders.append(self.handle_output(instance))

        return renders

    # This should be updated later to have more options
    # Split EXPORT_IMAGE to be able to use IO in per user folders
    # For now, images will be returned as IOBytes, and  Embedded will be returned as an HTML tag
    def handle_output(self, renderer : BaseRenderer) -> Render:
        render = Render(None, RendererOutputType.ERROR_NOT_SET)
        if renderer.output_type == RendererOutputType.EXPORT_IMAGE_BYTES:
            output : BytesIO = renderer.render()
            output.seek(0)
            # TODO the data pre-utf8 decode loooks nearly identical but doesnt work, investigate later
            render.data = base64.b64encode(output.getvalue()).decode("utf-8").replace("\n", "") # this might not be very optimal, check later
            render.type = RendererOutputType.EXPORT_IMAGE_BYTES
        elif renderer.output_type == RendererOutputType.EMBEDDED:
            # this should already be an embeddable string that can be inserted as an HTML tag
            render.type = RendererOutputType.EMBEDDED
            render.data = renderer.render()
            
        return render




# TODO finish abstractified version of this to support loading renderers at runtime
""" class Renderservice():
    renderers = {}

    def __init__(self) -> None:
        self.renderers["mpl"] = lambda x : create_renderer(x, self.create_renderer_settings(x), RendererOutputType.EXPORT_IMAGE, MPLRenderer)
        self.renderers["plotly"] = lambda x: create_renderer("plotly", RendererSettings(), RendererOutputType.EMBEDDED, PlotlyRenderer)

    def get_renderer(self, renderer_name: str) -> BaseRenderer:
        if renderer_name not in self.renderers:
            raise ValueError("Invalid renderer selected")

        return self.renderers[renderer_name]()

    def get_renderer_names(self) -> List[str]:
        return list(self.renderers.keys())

    def create_renderer_settings(self, renderer_name: str) -> RendererSettings:
        return RendererSettings()

    def add_renderer(self, renderer_name: str, lambda_renderer: Callable[[], BaseRenderer], lambda_settings: Callable[[], RendererSettings]) -> None:
        if renderer_name in self.renderers or renderer_name in self.renderer_settings:
            raise ValueError("A renderer with this name already exists")
        
        self.renderers[renderer_name] = lambda_renderer
        self.renderer_settings[renderer_name] = lambda_settings """





