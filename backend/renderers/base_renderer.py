from abc import ABC,  abstractmethod

from enum import Enum

from typing import List

from backend.commons.t2t_enums import RendererPaginationSetting

from ..commons.parser_commons import ParserOutput


class RendererSettings(object):
    EXPORT_IMAGE_FILE_PATH : str

    def __init__(self):
        pass


class RendererOutputType(Enum):
    LIBRARY_NATIVE = 1,
    EXPORT_IMAGE_FILE = 2,
    EXPORT_IMAGE_BYTES = 3,
    EMBEDDED = 4,
    ERROR_NOT_SET = 5


class BaseRenderer(ABC):

    # Typing is brea
    @abstractmethod
    def accept(self, parser_output: ParserOutput, pagination_setting : RendererPaginationSetting=RendererPaginationSetting.PAGES):

        raise NotImplemented

    @abstractmethod
    def render(self):

        # separated from accept since some renderers might be
        # generating a file/embeddable javascript

        raise NotImplemented

    @property
    @abstractmethod
    def settings(self):

        return self._settings

    @settings.setter
    def settings(self, settings: RendererSettings):

        self._settings = settings

    @property
    @abstractmethod
    def output_type(self):

        return self._output_type

    @output_type.setter
    def output_type(self, ot: RendererOutputType):

        self._output_type = ot

    @abstractmethod
    def render_next_page(self):

        raise NotImplemented

    @abstractmethod
    def render_pages(self):

        raise NotImplemented
