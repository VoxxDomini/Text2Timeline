from ast import Set
import spacy
import re

from typing_extensions import override
from typing import List, Tuple, Dict, Set

from .base import BaseParser
from ..commons.temporal import TemporalEntity, TemporalEntityType
from ..commons.parser_commons import ParserInput, ParserOutput, ParserSettings

from ..commons.t2t_logging import log_error, log_info


SPACY_PARSER_NAME = "spaCy"

class SpacyParser(BaseParser):
    _SPACY_TEMPORAL_TAGS: List[str] = ["DATE", "TIME"]
    _TEMPORAL_ERROR: str = "ERROR GETTING DATE/YEAR"
    _PARSER_NAME: str = SPACY_PARSER_NAME

    def __init__(self):
        self._settings = ParserSettings() # all default values
        self.initialize()

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings: ParserSettings):
        self._settings = settings

    @override
    def accept(self, input: ParserInput, contains_no_year_temporals=True, batch_mode=False, batch_offset=-1) -> ParserOutput:
        # BIG TODO, move all class state into a short lifecycle context object
        # since multiple requests actually works surprisingly well might as well clean up all the race conditions
        
        self.input = input
        self._contains_no_year_temporals = contains_no_year_temporals and not batch_mode
        self._batch_mode = batch_mode
        self._batch_offset = batch_offset

        # Don't do any post processing after ParseOuput is instanciated
        # as the ouput will be appended to another output as part of the batching process
        intermediate_outputs = not batch_mode

        if self._batch_mode:
            self.validate_batch_mode()

        tempora_entity_list: List[TemporalEntity] = []

        spacy_document = self.init_document()
        
        tempora_entity_list = self.extract_temporals(spacy_document)

        output: ParserOutput = ParserOutput(tempora_entity_list, contains_no_year_temporals=self._contains_no_year_temporals, finalizeOnInit=intermediate_outputs)
        output.parser_name = self._PARSER_NAME

        self.teardown_and_cleanup()
        return output

    def validate_batch_mode(self) -> None:
        if self._batch_offset == -1:
            log_error("Parser batch mode turned on but no batch information set")
            raise ValueError("NO BATCH INFORMATION SET IN PARSER")

    def extract_temporals(self, spacy_document) -> List[TemporalEntity]:
        tempora_entity_list: List[TemporalEntity] = []
        processed_events: Set = set() 
        counter : int = 0
        last_valid_year : str = ""

        if self._batch_mode:
            counter += self._batch_offset + 1

        for entity in spacy_document.ents:
            if entity.label_ in self._SPACY_TEMPORAL_TAGS:
                date = entity.text
                event = entity.sent.text

                result_year = self.get_year(date)
                temporal_value = self.format_year(result_year)

                if temporal_value is not None and event not in processed_events:
                    processed_events.add(event) 

                    temporal_entity: TemporalEntity = TemporalEntity()
                    temporal_entity.event = event
                    temporal_entity.date = date
                    temporal_entity.year = temporal_value
                    temporal_entity.order = counter
                    self.populate_context(temporal_entity, entity.sent.start)
                    tempora_entity_list.append(temporal_entity)

                    last_valid_year = temporal_value
                elif event not in processed_events:
                    processed_events.add(event)
                    temporal_entity: TemporalEntity = TemporalEntity()
                    temporal_entity.event = event
                    temporal_entity.date = date
                    temporal_entity.entity_type = TemporalEntityType.NO_YEAR
                    temporal_entity.order = counter
                    self.populate_context(temporal_entity, entity.sent.start)
                    temporal_entity._year_before = last_valid_year
                    tempora_entity_list.append(temporal_entity)

                counter += 1



        return tempora_entity_list

    def populate_context(self, temporal_entity: TemporalEntity, sentence_start):
        context_radius = self._settings.context_radius

        if context_radius == 0:
            return

        sentence_index = self._sentence_start_to_index_map[sentence_start]

        for x in range(1, context_radius+1):
                        if (sentence_index - x) > 0:
                            temporal_entity.context_before += str(self._sentences[sentence_index - x]) + " "
                        if (sentence_index + x) < self._sentence_size:
                            temporal_entity.context_after += str(self._sentences[sentence_index + x]) + " "


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
            year = re.search('([0-9]{1,2})', date_text)
            if year is not None:
                year = (int(year.group(1)) -1) * 100
                if year == 0:
                    year = 1
                result_year = str(year)

        # manually editted to remove false positives because of weaker model than the heavier/slower ones
        years = re.findall(r'(?<![\[])([0-9]{3,4})(?![\]])', date_text) 
        
        if len(years) > 0:
            for y in years:
                if len(y) >= 3:
                    if all(v == '0' for v in y) is False:
                        result_year = str(y)

        return result_year
    

    @override
    def initialize(self):
        self._nlp = spacy.load("en_core_web_sm")
        
    def teardown_and_cleanup(self) -> None:
        try:
            del self._sentences
            del self._sentence_start_to_index_map
        except:
            pass

    def init_document(self):
        document = self._nlp(self.input.get_content()) # expects non-tokenized text
        self._sentences = list(document.sents)

        self._sentence_start_to_index_map: Dict[int, int] = {}

        for index, sentence in enumerate(self._sentences):
            self._sentence_start_to_index_map[sentence.start] = index # type: ignore

        self._sentence_size = len(list(document.sents))
        return document