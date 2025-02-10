

from backend.commons.parser_commons import ParserOutput


class example_postprocessorX:
    def __init__(self):
        pass

    def process(self, parser_output: ParserOutput):
        x = parser_output.content

        for xx in x:
            xx.year = "500"

        