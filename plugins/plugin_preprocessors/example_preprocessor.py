from backend.commons.parser_commons import ParserInput


class example_preprocessor:
    plugin_description = "This is an example preprocessor, it will run on the input right before the selected parser receives it. This one does nothing though :)"


    def __init__(self):
        pass

    def process(self, parser_input: ParserInput):
        parser_input._content = str.upper(parser_input._content)
        pass