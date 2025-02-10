

from backend.commons.parser_commons import ParserOutput


class example_postprocessor:
    plugin_description = "Will reprocess the parser outputs using spaCy to properly resolve sentences with multiple dates, trying to pick the most suitable one"

    def __init__(self):
        self.processor_order = 5
        pass

    def process(self, parser_output: ParserOutput):
        """ x = parser_output.content

        for xx in x:
            xx.year = "500" """
        pass

        