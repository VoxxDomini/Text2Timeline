from typing import List, Dict

from nltk.sem.logic import EntityType

from backend.commons.t2t_logging import log_decorated, log_error, log_info
from ..commons.temporal import TemporalEntity, TemporalEntityType

import re

class ParserSettings(object):
    def __init__(self, context_radius: int = 0, name: str = "NAME_NOT_SET"):
        self._context_radius = context_radius

    @property
    def context_radius(self):
        return self._context_radius
    
    @context_radius.setter
    def context_radius(self, radius: int):
        self._context_radius = radius


import nltk

# TODO check whether this being here is more efficient as opposed to only in the class 
tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')

class ParserInput():
    _tokenizer = tokenizer

    def __init__(self, content):
        self._content = content

    def tokenize(self):
        self._content = self._tokenizer.tokenize(self._content) # type: ignore

    def remove_citations(self):
        pass
    
    # removes Wikipedia-style citations that look like this [123]
    def remove_citation_numbers(self):
        self._content = re.sub(r'\[\d+\]', '', self._content)

    def get_content(self):
        # parsers should use this in case some mandatory preprocessing has to be added
        return self._content

    def get_in_batches(self, batch_size):
        batches = []
        total_items = len(self._content)
        
        for i in range(0, total_items, batch_size):
            batches.append(ParserInput(self._content[i:i+batch_size]))
        
        if len(batches) > 1 and len(batches[-1]._content) < batch_size:
            last_batch = batches.pop()  
            batches[-1]._content += last_batch._content  
        
        log_decorated(f"Batching size: {batch_size} / {total_items} resulting in {len(batches)} batches")
        return batches

    def get_in_batches_by_percentage(self, percentage):
        if not (0 < percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100")

        total_items = len(self._content)
        batch_size = max(1, int((percentage / 100) * total_items))
        return self.get_in_batches(batch_size)




class ParserOutput(object):

    def __init__(self, content: List[TemporalEntity], contains_no_year_temporals : bool = False, batch_mode=False, finalizeOnInit=True):
        self._content = content
        self.page_size = 20
        self.current_page = 1
        self.parser_name = ""
        self.elapsed_time: float

        self._no_year_temporals = contains_no_year_temporals
        self._batch_mode = batch_mode
        self._finalized = False
        self._last_batch_max_order = 0

        """
            Many of these are for backwards compatibility with dumbed-down versions of the parser, which should also
            still support the previous ways they worked in (no non-year temporals, no batching)
            keeping it in in case I want to add a config file to compare the modes later

            The ParserOuput defaults represent the bare minimum functionality of running the parsers, as should the defaults
            in the parsers themselves
        """
        if finalizeOnInit:
            self.finalize_after_init()

    def finalize_after_init(self):
        if self._no_year_temporals and self._batch_mode == False:
            self.prepare_non_year_temporals()
        
        if self._batch_mode == False:
            self.sort_asc()

    @property
    def content(self) -> List[TemporalEntity]:
        if self._batch_mode == True and self._finalized == False:
            log_error("Batch mode content is locked until output is finalized")
            return []
        return self._content

    @content.setter
    def content(self, content: List[TemporalEntity]):
        self._content = content

    def append_content(self, new_output) -> None:
        '''
            The idea behind this is that with batching turned on, any final operations should be run
            once all content has been added
        '''
        if self._batch_mode == False:
            log_error("Attempting to change parser output with batching turned off")
            return

        if new_output == None or len(new_output.content) == 0:
            log_decorated(str(new_output))
            #log_info("Null output appended in batch mode, exiting")
            return

        new_content = new_output.content
        log_decorated("Appending content with length "+str(len(new_content)))
        self._last_batch_max_order = new_content[-1].order
        self._content.extend(new_content)

    def finalize(self) -> None:
        self._finalized = True

        if self._no_year_temporals:
            self.prepare_non_year_temporals()

        self.sort_asc()
        

    def __len__(self):
        return len(self._content)

    def __str__(self):
        result: str = ""
        result += f"{self.parser_name}\n---------------------\n";
        for temporal_entity in self.content:
            result += str(temporal_entity) + "\n"

        return result

    def year_map(self) -> Dict[int, List[TemporalEntity]]:
        if self._year_map is not None:
            return self._year_map

        year_map = {}
        for temporal_entity in self.content:
            if temporal_entity.year not in year_map:
                year_map[temporal_entity.year] = []

            year_map[temporal_entity.year].append(temporal_entity)
        
        self._year_map = year_map
        return self._year_map

    def years(self) -> List[int]:
        if self._years is not None:
            return self._years

        year_map = self.year_map()
        years: List[int] = list(year_map.keys())
        years = sorted(years)
        self._years = years

        return self._years

    def prepare_non_year_temporals(self) -> None:
        data_yes_years = [i for i in self.content if i.entity_type == TemporalEntityType.WITH_YEAR]
        data_no_years = [i for i in self.content if i.entity_type == TemporalEntityType.NO_YEAR]

        self.content = data_yes_years
        self.content_no_years = data_no_years

    # list splicing is inclusive beginning non-inclusive end
    def get_current_page(self) -> List[TemporalEntity]:
        index = (self.current_page - 1) * self.page_size
        return self._content[index:index+self.page_size]

    def next_page(self) -> List[TemporalEntity]:
        if self.current_page * self.page_size >= len(self.content):
            self.current_page = 0

        current_page = self.get_current_page()
        self.current_page += 1

        return current_page

    def has_next_page(self) -> bool:
        if (self.current_page + 1) * self.page_size >= len(self.content):
            return False
        
        return True

    def sort_asc(self):
        self._content = sorted(self._content, key=lambda x: int(x.year))