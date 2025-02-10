from enum import Enum

# TODO move all the globals here because python imports are going in circles

DEFAULT_RENDERER_MPL = "MPL"
DEFAULT_RENDERER_PLOTLY = "PLOTLY"

class RendererPaginationSetting(Enum):
    SINGLE_IMAGE = 1,
    PAGES = 2

class PluginType(Enum): # these also act as plugin folder naming conventions
    PLUGIN_PARSER = "plugin_parsers"
    PLUGIN_RENDERER = "plugin_renderers"
    PLUGIN_PREPROCESSOR = "plugin_preprocessors"
    PLUGIN_POSTPROCESSOR = "plugin_postprocessors"
    PLUGIN_GALLERYEXTRA = "plugin_galleryextras"