from backend.parsers.allennlp import AllennlpParser
from backend.commons.parser_commons import ParserInput, ParserOutput, ParserSettings
from backend.parsers.base import BaseParser
from backend.commons.output_exports import CSVExporter

from backend.parsers.spacy import SpacyParser
from backend.renderers.base_renderer import RendererOutputType
from backend.renderers.mpl import MPLInteractiveRenderer, MPLRenderer
from backend.renderers.plotly import PlotlyRenderer
from backend.commons.output_statistics import compare_parser_ouputs
from backend.parsers.flairparser import FlairParser

from backend.commons.t2t_logging import initialize_logging, log_info

import time


with open("resources/texts/Germany.txt", 'r') as file:
        loaded = file.read()


initialize_logging()


settings: ParserSettings = ParserSettings()
settings.context_radius = 2


parser_input: ParserInput = ParserInput(loaded)
parser_input.remove_citation_numbers()


parser = FlairParser()
parser.settings = settings


start_time = time.perf_counter()
parser_result: ParserOutput = parser.accept(parser_input)
parser_result.elapsed_time = time.perf_counter() - start_time

log_info(f"{parser_result.parser_name} took: {parser_result.elapsed_time}")



mpl_renderer = PlotlyRenderer()
mpl_renderer.accept(parser_result)
mpl_renderer.output_type = RendererOutputType.LIBRARY_NATIVE
mpl_renderer.render()

print("HLELO")


""" 

spacy_parser: SpacyParser = SpacyParser()
spacy_parser.settings = settings

parser: AllennlpParser = AllennlpParser()
parser.settings = settings

start_time = time.perf_counter()
allen_nlp_result: ParserOutput = parser.accept(parser_input)
allen_nlp_result.elapsed_time = time.perf_counter() - start_time


#print("Comparing")
#compare_parser_ouputs(spacy_result,allen_nlp_result)


mpl_renderer = PlotlyRenderer()
mpl_renderer.accept(spacy_result)
mpl_renderer.output_type = RendererOutputType.LIBRARY_NATIVE
mpl_renderer.render_next_page()



exporter: CSVExporter = CSVExporter()
exporter.export("output_allenlp", allen_nlp_result)
exporter.export("output_spacy", spacy_result)
print("Exports Done!")
print("allen: " + str(allen_nlp_result.elapsed_time))
print("spacy: " + str(spacy_result.elapsed_time))

# TODO remove duplicate events from spacy parser """
