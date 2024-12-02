from typing import List, Dict
from ..commons.temporal import TemporalEntity

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

class ParserInput():
    _tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')

    def __init__(self, content):
        self._content = content
        self._raw = content

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




class ParserOutput(object):

    def __init__(self, content: List[TemporalEntity]):
        self._content = content
        self.page_size = 20
        self.current_page = 1
        self.parser_name = ""
        self.elapsed_time: float

        self.sort_asc()

    @property
    def content(self) -> List[TemporalEntity]:
        return self._content

    @content.setter
    def content(self, content: List[TemporalEntity]):
        self._content = content

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