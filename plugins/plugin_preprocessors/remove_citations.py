from backend.commons.parser_commons import ParserInput
import re

class remove_citations:
    plugin_description = "Removes wikipedia-style citations from input text."

    def __init__(self):
        pass

    def process(self, parser_input: ParserInput):
        parser_input._content = self.remove_wikipedia_citations(parser_input._content)

    def remove_wikipedia_citations(self, parser_content):
        pattern = r'\[\s*(?:[0-9]+|citation needed|[\w\s]+)\s*\]'
        cleaned_text = re.sub(pattern, '', parser_content)
        
        return cleaned_text