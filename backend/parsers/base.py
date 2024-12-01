from abc import ABC,  abstractmethod
from ..commons.parser_commons import ParserInput, ParserOutput, ParserSettings

# TODO Split parsers to internal and external, so that "plugin" parsers can be added and ran in their own environment, and add their outputs to a folder to be
# picked up by statistics services

class BaseParser(ABC):
    @abstractmethod
    def accept(self, input: ParserInput) -> ParserOutput:
        raise NotImplemented

    @abstractmethod
    def initialize(self) -> None:
        raise NotImplemented

    @property
    @abstractmethod
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings: ParserSettings):
        self._settings = settings
