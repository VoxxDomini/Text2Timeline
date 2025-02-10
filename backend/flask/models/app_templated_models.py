

from enum import Enum
from backend.commons.parser_commons import ParserOutput
from backend.commons.t2t_logging import log_decorated
from backend.commons.temporal import TemporalEntity
from backend.renderers.base_renderer import RendererOutputType
from typing import List



class RenderPlacement(Enum):
    GALLERY = 1,
    INTERACTIVE = 2,
    EXTRAS = 3,
    NOT_SET = 4

class Render():
    
    def __init__(self, data, otype: RendererOutputType):
        self.data = data
        self.type = otype
        self.placement : RenderPlacement = RenderPlacement.NOT_SET # I'll use this to have additional filtering apart from data type for FE placement


class ResultPageModel():
    

    def __init__(self, use_pagination: bool):
        self._use_pagination = use_pagination
        self.renders : List[Render] = []
        self.output : ParserOutput
        self.flavor_text: str = "" # for any FE pages that require a dynamic description, just add here as embedded html

    def get_gallery(self):
        bytes = []
        for r in self.renders:
            if r.type == RendererOutputType.EXPORT_IMAGE_BYTES and r.placement == RenderPlacement.GALLERY:
                bytes.append(r.data)

        return bytes

    def get_extras(self):
        bytes = []
        for r in self.renders:
            if r.type == RendererOutputType.EXPORT_IMAGE_BYTES and r.placement == RenderPlacement.EXTRAS:
                bytes.append(r.data)

        return bytes

    def get_temporal_list(self) -> List[TemporalEntity]:
        return self.output.get_current_page() if self._use_pagination else self.output.content

    def get_temporal_list_no_years(self) -> List[TemporalEntity]:
        return self.output.content_no_years # TODO add pagination to this

    def get_embedded_renders(self):
        return [i.data for i in self.renders if i.type == RendererOutputType.EMBEDDED]


class PluginInformationModel():
    def __init__(self):
        self.pre_processors = []
        self.post_processors = []
        self.gallery_extras = []
        self.parsers = []
        pass

