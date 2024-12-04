from enum import Enum

# TODO move all the globals here because python imports are going in circles

DEFAULT_RENDERER_MPL = "MPL"
DEFAULT_RENDERER_PLOTLY = "PLOTLY"

class RendererPaginationSetting(Enum):
    SINGLE_IMAGE = 1,
    PAGES = 2
