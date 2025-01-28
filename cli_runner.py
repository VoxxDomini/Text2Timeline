import re
from typing import List

from click import parser
from backend.commons.parser_commons import ParserInput
from backend.commons.t2t_enums import RendererPaginationSetting
from backend.renderers.base_renderer import RendererOutputType
from backend.services import parserservice, renderservice
from backend.commons.utils import word_list_to_string
from backend.commons.parser_commons import ParserInput
from backend.renderers.mpl import MPLInteractiveRenderer
from backend.commons.t2t_logging import initialize_logging

def run_cli() -> None:
    initialize_logging()

    parser_service = parserservice.ParserService()
    renderer_service = renderservice.RendererService()

    selected_parser = ""
    selected_renderer = ""

    parser_list = parser_service.get_parser_names()
    print_possible_selections(parser_list)

    while is_valid_selection(selected_parser, parser_list) == False:
        selected_parser = input("Select a parser  ")

    numeric_to_selection_temp = print_selected(selected_parser, parser_list)
    if numeric_to_selection_temp is not None:
        selected_parser = numeric_to_selection_temp

    # well technically I can get plotly to render locally but for now just doing
    # the local mpl implementation since it took so much time

    """ renderer_list = renderer_service.get_renderer_names()
    while is_valid_selection(selected_renderer, renderer_list) == False:
        selected_renderer = input("Select a renderer  ") """

    print("Using MPL renderer")

    input_path = ""
    while is_valid_selection(input_path) == False:
        input_path = input("Path to file  ")

    input_content = load_input_file(input_path)
    parser_input: ParserInput = ParserInput(input_content)

    parser_output = parser_service.parse_with_selected(parser_input, selected_parser)

    # replace this managed rendering if plotly is implemented
    # for now, local mpl rendering for the full cli experience
    renderer = MPLInteractiveRenderer()
    renderer.accept(parser_output, RendererPaginationSetting.SINGLE_IMAGE)
    renderer.output_type = RendererOutputType.LIBRARY_NATIVE

    renderer.render_pages()



    



def is_valid_selection(selection: str, possible_selections: List = []):
    valid_string = selection is not None and  selection != "" and  str.strip(selection) != ""
    if possible_selections:
        valid_selection = str(selection) in possible_selections or ( selection.isnumeric() and int(selection)-1 < len(possible_selections) )
    else:
        valid_selection = True
    return valid_string and valid_selection


def print_possible_selections(selections) -> None:
    print("**************")
    for i, selection in enumerate(selections):
        print(f"* ({str(i+1)})  {selection}")
    print("*")
    print("*")
    print("*")
    print("**************")


def print_selected(selection: str, possible_selections: List) -> None:
    print("Selected ", end="")
    if selection.isnumeric():
        print(possible_selections[int(selection)-1])
        return possible_selections[int(selection)-1]
    else:
        print(selection)
        return None
    

def load_input_file(path: str): # no typing because str | None requires python 3.10, TODO see how many things the update breaks
    try:
        with open(path, 'r') as file:
            lines = file.readlines()
        return word_list_to_string(lines)
    except FileNotFoundError:
        print(f"Error: File not found at path: {path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None