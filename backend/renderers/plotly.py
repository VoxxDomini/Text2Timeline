import plotly.graph_objects as go
import io
from base64 import b64encode
from typing_extensions import override

from backend.commons.temporal import TemporalEntity

from .base_renderer import BaseRenderer, RendererOutputType, RendererSettings
from ..commons.parser_commons import ParserOutput, ParserInput
from typing import List


class PlotlyRenderer(BaseRenderer):
    _RENDERER_NAME : str = "PLOTLY"
    
    @override
    def accept(self, parser_output: ParserOutput):
        self._parser_output = parser_output
        self.build_plot(self._parser_output.get_current_page())

    @override
    def render(self):
        if self._output_type == RendererOutputType.LIBRARY_NATIVE:
            self._fig.show()
        elif self._output_type == RendererOutputType.EMBEDDED:
            buffer = io.StringIO()
            self._fig.write_html(file=buffer,include_plotlyjs=False, full_html=False)
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
        self.build_plot(self._parser_output.next_page())
        self.render()

    @override
    def render_pages(self):
        while self._parser_output.has_next_page():
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
                textfont=dict(size=14)  # Set the text size
            ))

        # Setting layout properties
        fig.update_layout(
            title="Timeline of Events",
            showlegend=False,
            width=1920,
            height=1080
            #plot_bgcolor='rgba(255, 255, 255, 255)'  # Set plot background color (transparent)
        )

        # Adjusting the x-axis grid properties
        if dates:
            fig.update_xaxes(
                showticklabels=True,
                showgrid=True,
                tickmode="array",
                tickvals=dates,
                ticktext=[str(d) for d in dates],  # Display years as tick labels
                tickfont=dict(color="black")
            )
        else:
            fig.update_xaxes(showticklabels=False, showgrid=False)

        # Hide the event axis label
        fig.update_yaxes(showticklabels=False, showgrid=False)  # Hide the y-axis

        fig.update_layout(
            paper_bgcolor='rgba(84,84,84,255)',
            plot_bgcolor='rgba(84,84,84,255)'
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


    def format_text(self, text, limit):
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
        result = list(set(result))
        return result