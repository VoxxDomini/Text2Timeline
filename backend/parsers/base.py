from abc import ABC,  abstractmethod
from ..commons.parser_commons import ParserInput, ParserOutput, ParserSettings


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
