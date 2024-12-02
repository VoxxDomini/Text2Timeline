

from backend.commons.parser_commons import ParserOutput
from backend.commons.temporal import TemporalEntity
from backend.renderers.base_renderer import RendererOutputType
from typing import List



class Render():
    def __init__(self, data, otype: RendererOutputType):
        self.data = data
        self.type = otype


class ResultPageModel():
    renders : List[Render] = []
    output : ParserOutput

    def __init__(self):
        pass

    def get_image_bytes(self):
        # each elemenent represents one image
        bytes = []
        for r in self.renders:
            if r.type == RendererOutputType.EXPORT_IMAGE_BYTES:
                bytes.append(r.data)

        return bytes

    def get_temporal_list(self) -> List[TemporalEntity]:
        return self.output.get_current_page()

    def get_temporal_list_no_years(self) -> List[TemporalEntity]:
        return self.output.content_no_years # TODO add pagination to this

    def get_embedded_renders(self):
        return [i.data for i in self.renders if i.type == RendererOutputType.EMBEDDED]