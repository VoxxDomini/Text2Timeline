from collections import defaultdict
from enum import Enum
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import plotly.graph_objects as go

import io
import base64

from backend.commons.parser_commons import ParserOutput
from backend.flask.models.app_templated_models import Render
from backend.renderers.base_renderer import RendererOutputType

"""
    All methods here to be used to generate additional plots as Render, the object used inside
    the ResultPage for rendering in the flask app.

    This can easily be decoupled for more general use with the raw image bytes by overriding
    functions to return the base64 data without wrapping it into a Render class
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


def get_matplotlib_as_bytes(plot) -> Render:
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

    # More pretty without labels :)
    #for i, count in enumerate(event_counts):
    #    plt.text(years[i], event_counts[i], str(count), ha='center', fontsize=10)

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    

    return get_matplotlib_as_bytes(plt)