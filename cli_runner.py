from operator import mul, pos
import re
from typing import List

from click import parser
from backend.commons.parser_commons import ParserInput
from backend.commons.t2t_enums import RendererPaginationSetting
from backend.renderers.base_renderer import RendererOutputType, RendererSettings
from backend.services import parserservice, renderservice, pipeline_manager_service
from backend.services.parser_comparison_service import ParserComparisonService
from backend.commons.utils import word_list_to_string
from backend.commons.parser_commons import ParserInput
from backend.renderers.mpl import MPLInteractiveRenderer, MPLRenderer
from backend.commons.t2t_logging import initialize_logging

def run_cli() -> None:
    initialize_logging()

    possible_selections = ["Generate Timeline", "Compare Parsers"]
    mode_select = ""
    while is_valid_selection(mode_select, possible_selections) == False:
        print_possible_selections(possible_selections)
        mode_select = input()

    if resolve_selection_text(mode_select, possible_selections) == possible_selections[0]:
        generate_timeline_flow()
    elif resolve_selection_text(mode_select, possible_selections) == possible_selections[1]:
        compare_parsers_flow()

    
def compare_parsers_flow():
    parser_service = parserservice.ParserService()
    parser_list = parser_service.get_parser_names()

    multi_select = []

    while len(multi_select) == 0:
        multi_select = get_multiple_selections(parser_list)

    parser_input = get_file_as_parser_input()

    parser_comparison_service = ParserComparisonService(parser_service)
    parser_comparison_service.parse_and_compare(multi_select, parser_input._content)

    # TODO local viewing and saving for this

    print(multi_select)


def generate_timeline_flow():
    pipeline_manager = pipeline_manager_service.PipelineManagerService()
    parser_service = pipeline_manager.parser_service

    selected_parser = ""

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

    parser_input = get_file_as_parser_input()

    parser_output = pipeline_manager.run_pipeline_parser_output(parser_input, selected_parser)

    possible_selections = ["View", "Export"]
    
    mode_select = ""
    while is_valid_selection(mode_select, possible_selections) == False:
        print_possible_selections(possible_selections)
        mode_select = input()

    if resolve_selection_text(mode_select, possible_selections) == possible_selections[0]:
        renderer = MPLInteractiveRenderer()
        #renderer = MPLRenderer()
        renderer.accept(parser_output, RendererPaginationSetting.SINGLE_IMAGE)
        renderer.output_type = RendererOutputType.LIBRARY_NATIVE
        renderer.render_pages()

    elif resolve_selection_text(mode_select, possible_selections) == possible_selections[1]:
        renderer = MPLRenderer()
        renderer.accept(parser_output, RendererPaginationSetting.PAGES)
        renderer.output_type = RendererOutputType.EXPORT_IMAGE_FILE
        renderer_settings = RendererSettings()
        renderer_settings.EXPORT_IMAGE_FILE_PATH = "./exports"
        renderer.settings = renderer_settings
        renderer.render_pages()


def get_file_as_parser_input() -> ParserInput:
    input_path = ""
    while is_valid_selection(input_path) == False:
        input_path = input("Path to file  ")

    input_content = load_input_file(input_path)
    parser_input: ParserInput = ParserInput(input_content)
    return parser_input



def is_valid_selection(selection: str, possible_selections: List = []):
    valid_string = selection is not None and  selection != "" and  str.strip(selection) != ""
    if possible_selections:
        valid_selection = str(selection) in possible_selections or ( selection.isnumeric() and int(selection)-1 < len(possible_selections) )
    else:
        valid_selection = True
    return valid_string and valid_selection


def print_possible_selections(selections) -> None:
    print("**************")
    print("*")
    print("*")
    print("*")
    for i, selection in enumerate(selections):
        print(f"* ({str(i+1)})  {selection}")
    print("*")
    print("*")
    print("*")
    print("**************")


def resolve_selection_text(selection: str, possible_selections):
    if str.isnumeric(selection):
        return possible_selections[int(selection)-1]
    return selection


def print_selected(selection: str, possible_selections: List) -> None:
    print("Selected ", end="")
    if selection.isnumeric():
        print(possible_selections[int(selection)-1])
        return possible_selections[int(selection)-1]
    else:
        print(selection)
        return None
    
def get_multiple_selections(possible_selections):
    EXIT_SIGNAL = "X"
    ALL_SIGNAL = "A"
    MESSAGE = "Select any of the following by typing its number and pressing enter. You will be able to select more until you enter " + EXIT_SIGNAL
    
    selections = []
    latest_selection = ""
    remaining_selections = possible_selections
    
    print("\n")
    print(MESSAGE)
    print("\n")
    while True:
        print(f"{ALL_SIGNAL}) All")
        print(f"{EXIT_SIGNAL}) Done")
        print_possible_selections(remaining_selections)

        latest_selection = input()

        if str.upper(latest_selection) == EXIT_SIGNAL or len(remaining_selections) == 0:
            break

        if latest_selection == str.upper(ALL_SIGNAL) or latest_selection == str.lower(ALL_SIGNAL):
            selections = possible_selections
            break

        if is_valid_selection(latest_selection, remaining_selections):
            selections.append(resolve_selection_text(latest_selection, remaining_selections))

        remaining_selections = [x for x in possible_selections if x not in selections]
    
    return selections



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