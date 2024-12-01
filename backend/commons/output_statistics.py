from .parser_commons import ParserOutput
from .temporal import TemporalEntity

from typing import List

def compare_parser_ouputs(output: ParserOutput, compare_to: ParserOutput):
    event_differences: int = 0

    bigger: ParserOutput
    smaller: ParserOutput

    if len(output) >= len(compare_to):
        bigger = output
        smaller = compare_to
    else:
        bigger = compare_to
        smaller = compare_to

    for i, x in enumerate(smaller.content):
        print(i, len(smaller))
        if x.event not in bigger.content:
            event_differences += 1

    print(bigger.parser_name, len(bigger))
    print(smaller.parser_name, len(smaller))
    print(smaller.parser_name + " contains " + str(event_differences) + " not contained in " + bigger.parser_name)




