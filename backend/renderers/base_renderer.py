from abc import ABC,  abstractmethod

from enum import Enum

from typing import List

from ..commons.parser_commons import ParserOutput


class RendererSettings(object):

    def __init__(self):
        pass



class RendererOutputType(Enum):
    LIBRARY_NATIVE = 1,
    EXPORT_IMAGE = 2,
    EMBEDDED = 3



class BaseRenderer(ABC):

    @abstractmethod

    def accept(self, parser_output: ParserOutput):

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



