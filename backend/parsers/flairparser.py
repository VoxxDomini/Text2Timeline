from flair.data import Sentence
from flair.models import SequenceTagger
from segtok.segmenter import split_single

from typing_extensions import override
from typing import List, Tuple, Dict

from .base import BaseParser
from ..commons.temporal import TemporalEntity
from ..commons.parser_commons import ParserInput, ParserOutput, ParserSettings

import re

class PredictionWrapper(object):
    def __init__(self, predicition: TemporalEntity, index: int):
        self.content = predicition
        self.sentence_index = index

class FlairParser(BaseParser):
    _FLAIR_TEMPORAL_TAG: str = "DATE"
    _TEMPORAL_ERROR: str = "ERROR GETTING DATE/YEAR"
    _PARSER_NAME: str = "Flair"

    def __init__(self):
        self._settings = ParserSettings() # all default values

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings: ParserSettings):
        self._settings = settings

    @override
    def accept(self, input: ParserInput) -> ParserOutput:
        self.input = input
        wrapped_prediction_list: List[PredictionWrapper] = []

        # keep inits barebones to potentially run in separate threads
        # move init out of here later, call it separately
        self.initialize()
        self.init_document()

        wrapped_prediction_list = self.extract_temporals(self._sentences)

        temporal_entity_list: List[TemporalEntity] = []
        temporal_entity_list = self.populate_context(wrapped_prediction_list)    

        output: ParserOutput = ParserOutput(temporal_entity_list)
        output.parser_name = self._PARSER_NAME
        return output

    def extract_temporals(self, spacy_document) -> List[PredictionWrapper]:
        wrapped: List[PredictionWrapper] = []
        processed_events: List[str] = []
        
        for sentence_index, sentence in enumerate(self._sentences): # type: ignore
            for entity in sentence.get_spans("ner"): # type:ignore
                if entity.tag == self._FLAIR_TEMPORAL_TAG:
                    date = entity.text
                    event = sentence.text # type: ignore


                    result_year = self.get_year(date)
                    temporal_value = self.format_year(result_year)


                    if temporal_value is not None and event not in processed_events:
                        # processed_events.append(event) # temporary solution to duplicate events due to spacy document structure

                        temporal_entity: TemporalEntity = TemporalEntity()
                        temporal_entity.event = event
                        temporal_entity.date = date
                        temporal_entity.year = temporal_value
                        wrap = PredictionWrapper(temporal_entity, sentence_index)
                        wrapped.append(wrap)



        return wrapped

    def populate_context(self, wrapped: List[PredictionWrapper]) -> List[TemporalEntity]:
        context_radius = self._settings.context_radius
        unwrapped: List[TemporalEntity] = []

        if context_radius == 0:
            return list(map(lambda n: n.content, wrapped))

        for wrapper in wrapped:
            sentence_index = wrapper.sentence_index
            for x in range(1, context_radius+1):
                            if (sentence_index - x) > 0:
                                wrapper.content.context_before += str(self._sentences[sentence_index - x].text) + " "
                            if (sentence_index + x) < len(self._sentences):
                                wrapper.content.context_after += str(self._sentences[sentence_index + x].text) + " "
            unwrapped.append(wrapper.content)

        return unwrapped


    def format_year(self, year):
        if year is None or year == self._TEMPORAL_ERROR:
            return None
        
        year = str(year)
        if len(year)==4:
            return year
        else:
            while len(year) < 4:
                year = "0"+year
            return year

    def get_year(self, date_text) -> str:
        result_year:str = self._TEMPORAL_ERROR

        if "century" in date_text:
            year = re.search('([1-9]{1,2})', date_text)
            if year is not None:
                year = (int(year.group(1)) -1) * 100
                if year == 0:
                    year = 1
                result_year = str(year)

        
        years = re.findall(r'(?<![\[])([0-9]{3,4})(?![\]])', date_text) # manually editted to remove false positives because of shittier model
        
        if len(years) > 0:
            for y in years:
                if len(y) >= 3:
                    if all(v == '0' for v in y) is False:
                        result_year = str(y)

        return result_year
    

    @override
    def initialize(self):
        self._model = SequenceTagger.load("ner-ontonotes")

    def init_document(self):
        # Might as well use the flair tokenizer instead of the nltk one
        tokenized = [Sentence(sent, use_tokenizer=True) for sent in split_single(self.input.get_content())]
        self._model.predict(tokenized)
        self._sentences = tokenized