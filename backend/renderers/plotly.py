import plotly.graph_objects as go
import io
from base64 import b64encode
from typing_extensions import override

from backend.commons.t2t_enums import RendererPaginationSetting
from backend.commons.temporal import TemporalEntity

from .base_renderer import BaseRenderer, RendererOutputType, RendererSettings
from ..commons.parser_commons import ParserOutput, ParserInput
from typing import List


class PlotlyRenderer(BaseRenderer):
    _RENDERER_NAME: str = "PLOTLY"

    @override
    def accept(self, parser_output: ParserOutput, pagination_setting: RendererPaginationSetting = RendererPaginationSetting.PAGES):
        self._parser_output = parser_output
        self.build_plot(self._parser_output.content)

    @override
    def render(self):
        if self._output_type == RendererOutputType.LIBRARY_NATIVE:
            self._fig.show()
        elif self._output_type == RendererOutputType.EMBEDDED:
            buffer = io.StringIO()
            self._fig.write_html(
                file=buffer, include_plotlyjs=False, full_html=False)
            return buffer.getvalue()

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings: RendererSettings):
        self._settings = settings

    @property
    def output_type(self):
        return self._output_type

    @output_type.setter
    def output_type(self, ot: RendererOutputType):
        self._output_type = ot

    @override
    def render_next_page(self):
        self.build_plot(self._parser_output.get_and_turn_page())
        self.render()

    @override
    def render_pages(self):
        while self._parser_output.current_page_exists():
            self.render_next_page()

    def build_plot(self, entity_list: List[TemporalEntity]):
        entities = sorted(entity_list, key=lambda x: int(x.year))
        fig = go.Figure()
        dates = self.get_date_list(entities)

        # Adding event markers with larger text
        for i, e in enumerate(entities):
            fig.add_trace(go.Scatter(
                x=[e.year],
                y=[self.pendulum(i)],
                mode="markers+text",
                name="TESTNAME",
                text=self.format_text(e.event, 25),
                hovertemplate="CONTEXT",
                textposition="bottom right",
                textfont=dict(size=14)
            ))

        fig.update_layout(
            title="Timeline of Events",
            showlegend=False,
            width=1920,
            height=1080,
        )

        # x-axis grid properties
        if dates:
            fig.update_xaxes(
                showticklabels=True,
                showgrid=True,
                tickmode="array",
                tickvals=dates,
                # Display years as tick labels
                ticktext=[str(d) for d in dates],
                tickfont=dict(color="black")
            )
        else:
            fig.update_xaxes(showticklabels=False, showgrid=False)

        fig.update_yaxes(showticklabels=False, showgrid=False)

        zoom_width = int(len(dates)/10)
        zoom_center = int(len(dates)/2)

        default_zoom_range = [dates[zoom_center],
                              dates[zoom_center+zoom_width]]
        
        # Default zoom works, pendulum needs some work
        fig.update_layout(
            paper_bgcolor='rgba(232, 232, 232, 255)',
            plot_bgcolor='rgba(232, 232, 232, 255)',
            xaxis={  
                'range': default_zoom_range,
                'type': 'linear'
            }
        )

        self._fig = fig

    def pendulum(self, value: int):
        # dont ask
        rem = value % 5
        if rem == 0:
            rem = 5

        if rem == 1:
            return 1
        elif rem == 2:
            return 3
        elif rem == 3:
            return 5
        elif rem == 4:
            return 7
        elif rem == 5:
            return 9

    def format_text(self, text, limit):  # replace with std text formatter used in mpl renderer
        s = text.split(" ")
        result = text.split(" ")

        char_count = 0
        for i, x in enumerate(s):
            char_count += len(x)
            if char_count >= limit:
                result.insert(i, "<br>")
                char_count = 0
        return " ".join(result)

    def get_date_list(self, entity_list):
        result = []
        for x in entity_list:
            result.append(int(x.year))
        result = sorted(list(set(result)))
        return result
