

from backend.commons.temporal import TemporalEntity
from backend.renderers.base_renderer import RendererOutputType
from typing import List



class Render():
    def __init__(self, data, otype: RendererOutputType):
        self.data = data
        self.type = otype


class ResultPageModel():
    renders : List[Render] = []
    outputs : List[TemporalEntity] = []

    def __init__(self):
        pass

    def get_image_bytes(self):
        # each elemenent represents one image
        bytes = []
        for r in self.renders:
            if r.type == RendererOutputType.EXPORT_IMAGE_BYTES:
                bytes.append(r.data)

        return bytes

    def get_temporal_list(self):
        text = []
        for t in self.outputs:
            text.append(str(t))

        return text