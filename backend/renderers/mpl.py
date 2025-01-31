from hashlib import new

from scipy.sparse import base
from backend.commons.t2t_enums import RendererPaginationSetting
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
from ..commons.t2t_logging import log_decorated, log_info

import textwrap

class AnnotationWrapper:
    def __init__(self, content: str, height: int, width: int):
        self.content = content
        self.height = height
        self.width = width

class MPLRenderer(BaseRenderer):
    _RENDERER_NAME : str = "MPL"
    _MAX_LINE_LENGTH = 60
    use_old_plot_algo = False

    @override
    def accept(self, parser_output: ParserOutput, pagination_setting:RendererPaginationSetting=RendererPaginationSetting.PAGES):
        self._parser_output = parser_output

        if pagination_setting == RendererPaginationSetting.PAGES:
            self.build_plot(self._parser_output.get_current_page())
        elif pagination_setting == RendererPaginationSetting.SINGLE_IMAGE:
            self.build_plot(self._parser_output.content)

    def __init__(self) -> None:
        super().__init__()
        self._text_wrapper = textwrap.TextWrapper()
                

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

        distance_between_min_max_years, min_date, max_date = self.calculate_interval(dates)
        
        # TODO batches get different intervals, is that bad? :(
        inter = int(distance_between_min_max_years / 20) # baseline interval

        log_decorated(f"Mpl Intervals, year range for this plot {distance_between_min_max_years}, baseline interval {inter}")

        names = []
        annotation_wrappers = []

        for e in temporal_entities:
            formatted, wrapped = self.format_and_add_metadata(e.event)
            names.append(formatted)
            annotation_wrappers.append(wrapped)
            

        names, dates = zip(*((name, date) for name, date in zip(names, dates) if int(date.year) > inter))
        
        if self.use_old_plot_algo:
            levels = self.generate_levels(len(dates), 10, 30)
        else:
            levels = self.generate_levels_2(dates, inter, annotation_wrappers, min_date)
    
        fig, ax = plt.subplots(figsize=(70, 10))

        ax.vlines(dates, 0, levels, color="tab:red")  # The vertical stems.

        ax.plot(dates, np.zeros_like(dates), "-o",
                color="k", markerfacecolor="w")  # Baseline and markers on it.

        # annotate lines
        last_top = None
        last_bot = None
        min_date_gap = int(distance_between_min_max_years / 12)

        for d, l, r in zip(dates, levels, names):
            h_align = "left"

            last = last_top if l > 1 else last_bot
            
            dif = 1000

            if last is not None:
                dif = abs(int((last-d).days/365))

            if last is not None and dif <= min_date_gap:
                h_align = "right"
            
            if self.use_old_plot_algo:
                ax.annotate(r, xy=(d, l),
                            xytext=(0, np.sign(l)*3), textcoords="offset points",
                            horizontalalignment=h_align,
                            verticalalignment="center" if l > 0 else "top"
                            )
            else: # current method
                ax.annotate(r, xy=(d, l),
                            xytext=(2, np.sign(l)*3), textcoords="offset points",
                            horizontalalignment="left",
                            verticalalignment="center" if l > 0 else "top"
                            )

            if l > 1:
                last_top = d
            else:
                last_bot = d

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

        self._plot = plt

    @override
    def render_next_page(self):
        plt.clf()
        plt.close()
        self.build_plot(self._parser_output.get_and_turn_page())
        self.render()

    @override
    def render_pages(self):
        while self._parser_output.has_next_page():
            self.render_next_page()
    
    def toggle_offset(self, offset):
        if offset == 0:
            return self._MAX_LINE_LENGTH * -1
        else:
            return 0

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

        # number of seconds in non-leap year 31536000 to get years, divmod returns tuple of quotient/remainder
        # so we want first element
        difference_in_years = divmod(difference.total_seconds(), 31536000)[0]

        return abs(difference_in_years), minDate, maxDate


    def format_and_add_metadata(self, text):
        wrapped_annotation : AnnotationWrapper = AnnotationWrapper(text, 0, 0)
    
        if len(text) > self._MAX_LINE_LENGTH:
            self._text_wrapper.max_lines = self._MAX_LINE_LENGTH
            formatted_text = self._text_wrapper.fill(text)
            wrapped_annotation.height = formatted_text.count("\n")
            wrapped_annotation.width = self._MAX_LINE_LENGTH
            return formatted_text, wrapped_annotation
        else:
            wrapped_annotation.height = 1
            wrapped_annotation.width = len(text)
            return text, wrapped_annotation

    def generate_levels(self, numberOfDates, numberOfLevels, levelRange):
        level_values = []
        step = 5
        current = 2

        for i in range(numberOfLevels):
            new_level = current
            level_values.append(new_level)
            level_values.append((new_level*-1))
            current += step
            if current >= levelRange:
                current = 2
            """ new_level = random.randrange(2,levelRange,2)
            level_values.append(new_level)
            level_values.append((new_level*-1)) """

        #level_values = [5,10,15,20,25,30,35,40] debug level to line height conversion

        levels = np.tile(level_values,
                        int(np.ceil(numberOfDates/len(level_values))))[:numberOfDates]
        return levels

    def generate_levels_2(self, dates, baseline_interval, annotation_wrappers: List[AnnotationWrapper], start_date):
        if len(dates) != len(annotation_wrappers):
            raise RuntimeError("Not good")

        if baseline_interval == 0:
            print("????????")
            return np.tile([10,20,30,40,50], len(dates))[:len(dates)]

        dates_numeric: List[int] = [dt.year for dt in dates]

        levels = []
        base_level = 5

        padding = 5
        
        current = base_level
        switch = 1

        index = 0
        max_height = 50

        last_date = None
        number_of_stacked_dates = 0
        stacked_date_extra_padding = 2

        level_map = {}

        for date, text_info in zip(dates_numeric, annotation_wrappers):
            current = base_level
            switch = 1

            divmod_tuple = divmod(date, baseline_interval*2) 
            # i realised way too late that this is kind of wrong, but I got it more or less working like this so whatever, eventually fix for edge cases
            # sections were supposed to be bigger and lookbehind being one section long only if remainder was above certain threshold, but this kinda works too
            section_key = divmod_tuple[0] 
            #print(f"*******GL2 date: {date} - skey:{divmod_tuple[0]} remainder:{divmod_tuple[1]}")

            if last_date == date:
                number_of_stacked_dates += 1
            else:
                number_of_stacked_dates = 0

            event_tuples_in_section = self.gl2_get_level_map_content_in_range(level_map, section_key, 2)
            if event_tuples_in_section is not None and len(event_tuples_in_section) > 0:
                event_tuples_in_section_sorted = sorted(event_tuples_in_section, key=lambda tuple: tuple[0])
                #print(f"GL2 {date} event being compared with {event_tuples_in_section_sorted}")
                min_c = 0
                for event_tuple in event_tuples_in_section_sorted:
                    if self.gl2_are_levels_touching(current, text_info.height, event_tuple[0], event_tuple[1]):
                        current = event_tuple[0] + text_info.height
                        current += padding
                        current += number_of_stacked_dates * stacked_date_extra_padding
                        min_c += 1
                        if current > max_height: # edge case here but its rare, eventually fix comparing minus switches to only other minuses
                            current = random.randint(base_level, 30) # randomly chosen 
                            switch *= -1
                            break
                #print(f"GL2 {date} was incremented {min_c} times")

            

            last_date = date
            bonus_padding = number_of_stacked_dates * stacked_date_extra_padding

            levels.append(current*switch)
            self.gl2_upsert_dict(level_map, section_key, (current, text_info.height, date)) 
            index += 1


        return levels

    # lookbehind sections in range
    def gl2_get_level_map_content_in_range(self, level_map, current, lookbehind_range):
        level_map_content = []

        lmap_keys = list(level_map.keys())

        if len(lmap_keys) == 0:
            return []

        # iterate backwards no more than 3 elements, why is python like this
        for i in range(len(lmap_keys) - 1, len(lmap_keys) - (lookbehind_range+1), -1):
            key = lmap_keys[i]
            if abs(current-key) > 3:
                #print(f"Breaking because current {current} too far from last {key} at cycle {i}")
                break

            level_map_content.extend(level_map[key])
            
        return level_map_content

        
            

    def gl2_are_levels_touching(self, clevel, cheight, pvlevel, pheight):
        if pvlevel - pheight <= clevel:
            #print(f"GL2 touching because {pvlevel} - {pheight} <= {clevel}")
            return True

        return False

    def gl2_are_widths_touching(self, cdate, pdate, interval):
        # i'm going to assume that a distance
        # of 60 max line width is around 2 intervals
        return pdate - cdate < interval * 2

    def gl2_upsert_dict(self, dict, key, val):
        if key in dict:
            dict[key].append(val)
        else:
            dict[key] = []
            dict[key].append(val)


    """ def generate_levels(self, dates, base_level=10, min_spacing=5):
        levels = [base_level]  # Start at base level
        for i in range(1, len(dates)):
            if abs((dates[i] - dates[i - 1]).days) < min_spacing:
                
                levels.append(levels[-1] + base_level)
            else:
                
                levels.append(base_level)
        return levels """








def zoom_factory(ax, base_scale=2.):
    prex = 0
    prey = 0
    prexdata = 0
    preydata = 0

    def zoom_fun(event):
        nonlocal prex, prey, prexdata, preydata
        curx = event.x
        cury = event.y

        if abs(curx - prex) < 10 and abs(cury - prey) < 10:
            xdata = prexdata
            ydata = preydata
        else:
            xdata = event.xdata 
            ydata = event.ydata 

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
            # zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # zoom out
            scale_factor = base_scale
        else:
            # sanity
            scale_factor = 1
            print(event.button)
        

        ax.set_xlim([
            xdata - cur_xrange * scale_factor,
            xdata + cur_xrange * scale_factor
        ])
        ax.set_ylim([
            ydata - cur_yrange * scale_factor,
            ydata + cur_yrange * scale_factor
        ])
        plt.draw()  # force re-draw

    fig = ax.get_figure()
    fig.canvas.mpl_connect('scroll_event', zoom_fun)

    return zoom_fun



class MPLInteractiveRenderer(BaseRenderer):
    @override
    def accept(self, parser_output: ParserOutput, pagination_setting : RendererPaginationSetting = RendererPaginationSetting.PAGES):
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
        self.build_plot(self._parser_output.get_and_turn_page())
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