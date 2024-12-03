from backend.commons.temporal import TemporalEntity
from .base_renderer import BaseRenderer, RendererSettings, RendererOutputType
from ..commons.parser_commons import ParserOutput

from typing import List
from typing_extensions import override

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import mplcursors

from ..commons.utils import get_export_file_path, join_folder_file_names

import random
from io import BytesIO
from ..commons.t2t_logging import log_info

class MPLRenderer(BaseRenderer):
    _RENDERER_NAME : str = "MPL"

    @override
    def accept(self, parser_output: ParserOutput):
        self._parser_output = parser_output
        self.build_plot(self._parser_output.get_current_page())
                

    @override
    def render(self):
        if self._output_type == RendererOutputType.LIBRARY_NATIVE:
            self._plot.show()
        elif self._output_type == RendererOutputType.EXPORT_IMAGE_FILE:
            if len(self.settings.EXPORT_IMAGE_FILE_PATH):
                # TODO custom exceptions
                raise ValueError("Attempting to save to file path with no path in renderer settings")

            #file_path = get_export_file_path(2, "timeline"+str(self._parser_output.current_page)+".png")
            file_path = join_folder_file_names(self.settings.EXPORT_IMAGE_FILE_PATH, "timeline"+str(self._parser_output.current_page)+".png")
            self._plot.savefig(file_path)
        elif self._output_type == RendererOutputType.EXPORT_IMAGE_BYTES:
            image_bytes = BytesIO()
            self._plot.savefig(image_bytes, format="png", bbox_inches="tight")
            self._plot.close()
            return image_bytes


    def build_plot(self, temporal_entities: List[TemporalEntity]):
        years = [x.year if x.year != '' else "0001" for x in temporal_entities]
        years = list(map(self.pad_year, years))
        dates = [datetime.strptime(d, "%Y") for d in years]
        interval = self.calculate_interval(dates)
        inter = int(interval / 20)

        names = []
        for e in temporal_entities:
            names.append(self.add_new_lines(e.event))


        names, dates = zip(*((name, date) for name, date in zip(names, dates) if int(date.year) > inter))

        levels = self.generate_levels(len(dates), 10, 30)
    
        fig, ax = plt.subplots(figsize=(50, 10))

        ax.vlines(dates, 0, levels, color="tab:red")  # The vertical stems.

        ax.plot(dates, np.zeros_like(dates), "-o",
                color="k", markerfacecolor="w")  # Baseline and markers on it.

        # annotate lines
        for d, l, r in zip(dates, levels, names):
            ax.annotate(r, xy=(d, l),
                        xytext=(0, np.sign(l)*3), textcoords="offset points",
                        horizontalalignment="left",
                        verticalalignment="center" if l > 0 else "top")

        # log_info("INTERVAL ERROR: " + str(dates))
        # log_info("INTERVAL ERROR: " + str(years))
        # log_info("INTERVAL ERROR: " + str(inter) + " from " + str(interval))

        # Some weird error when dates are too close together
        # instead of redoing the math, i'll do this!
        if inter == 0:
            inter = 1

        ax.xaxis.set_major_locator(mdates.YearLocator(inter))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

        # remove y-axis and spines
        ax.yaxis.set_visible(False)
        ax.spines[["left", "top", "right"]].set_visible(False)

        ax.margins(y=0.1)

        # This should only be available in the interactive version
        # Causes some weird threading issues when generating images
        # TODO move later
        # f = zoom_factory(ax)

        self._plot = plt

    @override
    def render_next_page(self):
        plt.clf()
        plt.close()
        self.build_plot(self._parser_output.next_page())
        self.render()

    @override
    def render_pages(self):
        while self._parser_output.has_next_page():
            self.render_next_page()

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
    def output_type(self, ot: RendererOutputType = RendererOutputType.LIBRARY_NATIVE):
        self._output_type = ot

    def pad_year(self, year):
        year = str(year)
        while len(year) < 4:
            year = "0" + year
        return year

    def calculate_interval(self, dates):
        sortedDates = sorted(dates)

        minDate = sortedDates[0]
        maxDate = sortedDates[-1]
        difference = minDate - maxDate

        difference_in_years = divmod(difference.total_seconds(), 31536000)[0]

        return abs(difference_in_years)


    def add_new_lines(self, text, limit=60):
        if len(text) > limit:
            return "\n".join(text[i:i+limit] for i in range(0, len(text), limit))
        else:
            return text

    def generate_levels(self, numberOfDates, numberOfLevels, levelRange):
        level_values = []
        for i in range(numberOfLevels):
            new_level = random.randrange(1,levelRange,3)
            level_values.append(new_level)
            level_values.append((new_level*-1))

        levels = np.tile(level_values,
                        int(np.ceil(numberOfDates/len(level_values))))[:numberOfDates]
        return levels





def zoom_factory(ax, base_scale=2.):
    prex = 0
    prey = 0
    prexdata = 0
    preydata = 0

    def zoom_fun(event):
        nonlocal prex, prey, prexdata, preydata
        curx = event.x
        cury = event.y

        # if not changed mouse position(or changed so little)
        # remain the pre scale center
        if abs(curx - prex) < 10 and abs(cury - prey) < 10:
            # remain same
            xdata = prexdata
            ydata = preydata
        # if changed mouse position ,also change the cur scale center
        else:
            # change
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location

            # update previous location data
            prex = event.x
            prey = event.y
            prexdata = xdata
            preydata = ydata

        # get the current x and y limits
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()

        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5

        # log.debug((xdata, ydata))
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)
        # set new limits
        ax.set_xlim([
            xdata - cur_xrange * scale_factor,
            xdata + cur_xrange * scale_factor
        ])
        ax.set_ylim([
            ydata - cur_yrange * scale_factor,
            ydata + cur_yrange * scale_factor
        ])
        plt.draw()  # force re-draw

    fig = ax.get_figure()  # get the figure of interest
    # attach the call back
    fig.canvas.mpl_connect('scroll_event', zoom_fun)

    # return the function
    return zoom_fun



class MPLInteractiveRenderer(BaseRenderer):
    @override
    def accept(self, parser_output: ParserOutput):
        self._parser_output = parser_output
        self.build_plot(self._parser_output.get_current_page())
                

    @override
    def render(self):
        if self._output_type == RendererOutputType.LIBRARY_NATIVE:
            self._plot.show()
        if self._output_type == RendererOutputType.EXPORT_IMAGE_FILE:
            file_path = get_export_file_path(2, "timeline"+str(self._parser_output.current_page)+".png")
            self._plot.savefig(file_path)


    def build_plot(self, temporal_entities: List[TemporalEntity]):
        entities = sorted(temporal_entities, key=lambda x: int(x.year))
        years = [int(e.year) for e in entities]

        plt.figure(figsize=(10, 6))
        line, = plt.plot(range(len(entities)), years, marker="o", linestyle="", color="blue")

        for i, e in enumerate(entities):
            # Add a small offset to the x-coordinate of the text label
            #plt.text(e.year + 0.2, i, e.event, va="center")
            pass

        plt.title("Timeline of Events")
        #plt.xlabel("Year")

        plt.ylim(min(years), max(years))
        plt.xticks([])
        #plt.xlim(-1, len(entities))

        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_visible(False)
        plt.gca().spines["left"].set_visible(False)

        mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(self.format_text(entities[sel.target.index].event, 50)))
        self._plot = plt

    @override
    def render_next_page(self):
        plt.clf()
        plt.close()
        self.build_plot(self._parser_output.next_page())
        self.render()

    @override
    def render_pages(self):
        while self._parser_output.has_next_page():
            self.render_next_page()

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
    def output_type(self, ot: RendererOutputType = RendererOutputType.LIBRARY_NATIVE):
        self._output_type = ot

    def format_text(self, text, limit):
        s = text.split(" ")
        result = text.split(" ")

        char_count = 0
        for i, x in enumerate(s):
            char_count += len(x)
            if char_count >= limit:
                result.insert(i, "\n")
                char_count = 0
        return " ".join(result)