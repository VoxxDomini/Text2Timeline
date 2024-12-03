import enum
from typing import List

from allennlp_models.pretrained import load_predictor

from .base import BaseParser
from typing_extensions import override
from ..commons.parser_commons import ParserInput, ParserOutput, ParserSettings
from ..commons.utils import word_list_to_string, disable_logging, log_decorator
from ..commons.temporal import TemporalEntity, TemporalEntityType

import re

class PredictionWrapper(object):
    # used to populate context from original text instead of predictions
    def __init__(self, predicition: dict, corpus_index: int):
        self.content = predicition
        self.corpus_index = corpus_index

ALLENNLP_PARSER_NAME = "allen_nlp"

class AllennlpParser(BaseParser):
    ALLENNLP_TEMPORAL_TAG = "ARGM-TMP"
    NO_DATE_DETECTED = "ERROR_NO_DATE"
    _PARSER_NAME = ALLENNLP_PARSER_NAME

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
    def accept(self, input: ParserInput) -> ParserOutput:
        self.input = input

        # currently this parsers needs to receive sentence-tokenized input
        self.input.tokenize()

        predictions = self.get_allennlp_predictions()


        tempora_entity_list = self.extract_temporal_parts(predictions)

        output = ParserOutput(tempora_entity_list, contains_no_year_temporals=True)
        output.parser_name = self._PARSER_NAME
        return output

    @disable_logging
    @override
    def initialize(self):
        self.predictor = load_predictor("structured-prediction-srl-bert")


    def get_allennlp_predictions(self) -> list:
        predictions = []
        for corpus_index, part in enumerate(self.input.get_content()):
            predictions.append(PredictionWrapper(self.predictor.predict(part), corpus_index))  # type: ignore

        return predictions

    def extract_temporal_parts(self, predictions: List[PredictionWrapper]) -> list:
        temporal_entity_list = []
        last_valid_year : str = ""
        counter = 0

        for prediction_wrapper in predictions:
            unwrapped: dict = prediction_wrapper.content # type: ignore

            for verb in unwrapped["verbs"]: 
                description = verb["description"]

                if self.ALLENNLP_TEMPORAL_TAG in description:
                    temporal_entity: TemporalEntity = self.handle_temporal_found(unwrapped, description)

                    if temporal_entity.year != self.NO_DATE_DETECTED:
                        temporal_entity.order = counter
                        counter += 1
                        last_valid_year = temporal_entity.year
                        self.append_context(temporal_entity, prediction_wrapper.corpus_index) # type: ignore
                        temporal_entity_list.append(temporal_entity)
                        # each prediction should be for a single sentence, in cases like
                        # "Between 12,900 and 11,700 years ago" we will store under the first value and skip the rest
                        break
                    else:
                        temporal_entity.order = counter
                        counter += 1
                        temporal_entity.entity_type = TemporalEntityType.NO_YEAR
                        temporal_entity._year_before = last_valid_year
                        self.append_context(temporal_entity, prediction_wrapper.corpus_index) # type: ignore
                        temporal_entity_list.append(temporal_entity)



        return temporal_entity_list

    def append_context(self, temporal_entity: TemporalEntity, corpus_index: int):
        context_radius = self._settings.context_radius

        if context_radius == 0:
            return

        corpus_size = len(self.input.get_content())

        for x in range(1, context_radius+1):
                        if (corpus_index - x) > 0:
                            temporal_entity.context_before += self.input.get_content()[corpus_index - x] + " "
                        if (corpus_index + x) < corpus_size:
                            temporal_entity.context_after += self.input.get_content()[corpus_index + x] + " "

    def handle_temporal_found(self, prediction: dict, description: str) -> TemporalEntity:
        temporal_entity = TemporalEntity()

        sentence = word_list_to_string(prediction["words"])

        temporal_entity.event = sentence

        year = self.extract_year(description)
        date = self.extract_date(description)

        temporal_entity.date = date
        temporal_entity.year = year

        return temporal_entity

    def extract_date(self, description) -> str:
        result = re.search('TMP(.*?)]', description)

        result_group = result.group(1)  # type: ignore

        result_group = result_group.replace("]", "")
        result_group = result_group.replace(":", "")

        return result_group

    def extract_year(self, description) -> str:
        result = re.search('TMP(.*?)]', description)

        result_group = result.group(1)  # type: ignore

        result_group = result_group.replace("]", "")
        result_group = result_group.replace(":", "")

        if "century" in result_group:
            year = re.search('([0-9]{1,2})', result_group)
            if year is not None:
                year = (int(year.group(1)) - 1) * 100
                return str(year)

        # fix this, detects days of month as years
        years = re.findall(r'(?<![\[])([0-9]{3,})(?![\]])', result_group)
        if len(years) > 0:
            for y in years:
                if len(y) >= 3:
                    if all(v == '0' for v in y) is False:
                        return str(y)

        # non_temporal_list.append(sentence)
        return self.NO_DATE_DETECTED



