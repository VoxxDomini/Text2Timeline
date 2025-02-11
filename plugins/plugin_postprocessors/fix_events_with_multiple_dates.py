import enum
from backend.commons.parser_commons import ParserOutput
import spacy
import re

'''
Currently, some of the default parsers will only detect the first occurrence of a phrase indicating a temporal event
in a sentence. This is due to how the context aggregation works, what we'll do is re-scan all collected NON-YEAR TEs
and see if they contain more than one date, if the date can be parsed and put on the timeline, the event will be moved.

We'll use spaCy for speed here, though honestly a sufficiently strong regex would also work.
'''
class fix_events_with_multiple_dates:
    processor_order = 1
    plugin_description = "Will reprocess the parser outputs using spaCy to properly resolve sentences with multiple temporal phrases, trying to pick the most suitable one"
    _SPACY_TEMPORAL_TAGS = ["DATE", "TIME"]

    def __init__(self):
        pass

    def process(self, parser_ouput: ParserOutput) -> None:
        if parser_ouput.content_no_years is None or len(parser_ouput.content_no_years) == 0:
            print("This parser output has no non-year temporals, plugin terminating early")
            return

        nlp = spacy.load("en_core_web_sm")
        
        indices_to_remove = []


        for i, x in enumerate(parser_ouput.content_no_years): 
            spacy_document = nlp(x.event)
            all_temporals = []

            for entity in spacy_document.ents:
                if entity.label_ in self._SPACY_TEMPORAL_TAGS:
                    all_temporals.append(entity.text)

            if len(all_temporals) <= 1:
                continue
            
            for t in all_temporals:
                parsed = self.parse_date(t)

                if parsed is not None:
                    # print("GREAT SUCCESS ", x.date, " to ", t, " ", x.event)
                    indices_to_remove.append(i)
                    x.date = t
                    x.year = parsed
                    x.toggle_entity_type() 
                    parser_ouput.content.append(x)
                    break
                    

        # surely there's a better way to do this
        for index in sorted(indices_to_remove, reverse=True):
            del parser_ouput.content_no_years[index]



    def parse_date(self, date_text):
        result_year = None

        if "century" in date_text:
            year = re.search('([0-9]{1,2})', date_text)
            if year is not None:
                year = (int(year.group(1)) -1) * 100
                if year == 0:
                    year = 1
                result_year = str(year)

        years = re.findall(r'(?<![\[])([0-9]{3,4})(?![\]])', date_text)

        if len(years) > 0:
            for y in years:
                if len(y) >= 3:
                    if all(v == '0' for v in y) is False:
                        result_year = str(y)
        
        if result_year is None:
            return None

        while len(result_year) < 4:
            result_year = "0"+result_year

        return result_year

            
