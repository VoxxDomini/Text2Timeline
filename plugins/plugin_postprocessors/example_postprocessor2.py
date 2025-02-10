

from backend.commons.parser_commons import ParserOutput


class example_postprocessor2:
    def __init__(self):
        self.processor_order = 9
        pass

    def process(self, parser_output: ParserOutput):
        x = parser_output.content

        for xx in x:
            xx.year = "700"

        