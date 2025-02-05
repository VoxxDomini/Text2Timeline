from collections import defaultdict
from enum import Enum
from typing import List
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import plotly.graph_objects as go

import io
import base64
import numpy as np

from backend.commons.parser_commons import ParserOutput
from backend.flask.models.app_templated_models import Render
from backend.renderers.base_renderer import RendererOutputType

"""
    All methods here to be used to generate additional plots as Render, the object used inside
    the ResultPage for rendering in the flask app.

    This can easily be decoupled for more general use with the raw image bytes by overriding
    functions to return the base64 data without wrapping it into a Render class

    EDIT:
    for now, i'll add all non main renderer (e.g. not replaceable through the plugin system for now) render methods here
    they should be fairly easy to extract later
"""

class ExtrasRenderer(Enum):
    MATPLOTLIB = 1,
    SEABORN = 2,
    PLOTLY = 3

class PlotType(Enum):
    SCATTER = 1,
    HEAT = 2,
    BARS = 3,
    BUBBLE =4

class DataSource(Enum):
    EVENTS_PER_YEAR = 1,
    TEMPORAL_PERCENTAGE = 2


def get_matplotlib_as_bytes(plot) -> Render: # use the fig api instead of plot as it's supposedly a bit more thread safe?
    image_bytes = io.BytesIO()
    plot.savefig(image_bytes, format="png", bbox_inches="tight")
    plot.close()
    image_bytes.seek(0)
    render = Render(None, RendererOutputType.ERROR_NOT_SET)
    render.data = base64.b64encode(image_bytes.getvalue()).decode("utf-8").replace("\n", "")
    render.type = RendererOutputType.EXPORT_IMAGE_BYTES
    return render

def get_seaborn_as_bytes(seabornFigure) -> Render:
    render = Render(None, RendererOutputType.ERROR_NOT_SET)

    buffer = io.BytesIO()
    seabornFigure.savefig(buffer, format="png")
    buffer.seek(0)
    render.data = base64.b64encode(buffer.getvalue()).decode("utf-8").replace("\n", "")
    render.type = RendererOutputType.EXPORT_IMAGE_BYTES

    return render


def events_per_year_bubble_mpl(parser_output:ParserOutput, group_size=0) -> Render:
    year_map = parser_output.year_number_map()
    
    years, event_counts = zip(*year_map.items())
    bubble_sizes = [count * 50 for count in event_counts]

    if group_size > 0:
        grouped_data = defaultdict(int)
        for year, count in year_map.items():
            group = (int(year) // group_size) * group_size  
            grouped_data[group] += count  

        years, event_counts = zip(*sorted(grouped_data.items()))
        
    bubble_sizes = [count * 50 for count in event_counts]
    plt.figure(figsize=(10, 6))
    plt.scatter(years, event_counts, s=bubble_sizes, alpha=0.6, color="skyblue", edgecolors="skyblue")

    plt.title("Event Counts by Year", fontsize=16)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Number of Events", fontsize=12)

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    return get_matplotlib_as_bytes(plt)


barchart_column_color_primary = "cyan"
barchart_column_color_secondary = "pink"

def parser_comparison_year_vs_no_year_grouped_bar_chart(parser_outputs: List[ParserOutput]): #barchart
    class_names = [parser.parser_name for parser in parser_outputs]
    num_year_temporals = [len(parser.content) for parser in parser_outputs]
    num_none_year_temporals = [len(parser.content_no_years) for parser in parser_outputs]

    bar_width = 0.35

    r1 = np.arange(len(class_names))
    r2 = [x + bar_width for x in r1]

    rects = plt.bar(r1, num_year_temporals, color=barchart_column_color_primary, width=bar_width, edgecolor='grey', label='Year Temporal Entities')
    rects2 = plt.bar(r2, num_none_year_temporals, color=barchart_column_color_secondary, width=bar_width, edgecolor='grey', label='No-Year Temporal Entities')

    autolabel_barchart_columns(plt, rects)
    autolabel_barchart_columns(plt, rects2)

    plt.xlabel('Parsers', fontweight='bold')
    plt.ylabel('Totals', fontweight='bold')
    plt.title('Comparison of year vs no-year temporals', fontweight='bold')
    plt.xticks([r + bar_width/2 for r in range(len(class_names))], class_names, rotation=45)
    plt.legend()
    plt.tight_layout()

    return get_matplotlib_as_bytes(plt)


def parser_comparison_execution_time(parser_outputs: List[ParserOutput]): #barchart
    class_names = [parser.parser_name for parser in parser_outputs]
    execution_times = [parser.elapsed_time for parser in parser_outputs]

    bar_width = 0.35
    r1 = np.arange(len(class_names))

    rects = plt.bar(r1, execution_times, color=barchart_column_color_primary, width=bar_width, edgecolor='grey', label='Execution time')
    autolabel_barchart_columns(plt,rects)

    plt.xlabel('Parsers', fontweight='bold')
    plt.ylabel('Time(s)', fontweight='bold')
    plt.title('Execution time', fontweight='bold')
    plt.xticks([r + bar_width/2 for r in range(len(class_names))], class_names, rotation=45)
  
    plt.tight_layout()

    return get_matplotlib_as_bytes(plt)


def parser_comparison_average_event_lengths(class_names, average_lengths): #barchart
    bar_width = 0.35
    r1 = np.arange(len(class_names))

    rects = plt.bar(r1, average_lengths, color=barchart_column_color_primary, width=bar_width, edgecolor='grey', label='Execution time')
    autolabel_barchart_columns(plt,rects)

    plt.xlabel('Parsers', fontweight='bold')
    plt.ylabel('Average Event Length', fontweight='bold')
    plt.title('Average Event Length', fontweight='bold')

    plt.xticks([r + bar_width/2 for r in range(len(class_names))], class_names, rotation=45)

    plt.tight_layout()

    return get_matplotlib_as_bytes(plt)


def autolabel_barchart_columns(plot, rectangles):
    downwards_offset = 10 # percentage but prob wont work for very low values?

    for rect in rectangles:
        height = rect.get_height()
        plt.annotate(f'{int(height)}', 
                    xy=(rect.get_x() + rect.get_width() / 2, height - int(height/downwards_offset)),  
                    xytext=(0, 3), 
                    textcoords="offset points",
                    ha='center', va='bottom')