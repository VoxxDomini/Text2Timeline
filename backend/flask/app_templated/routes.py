from math import log
from backend.commons.parser_commons import ParserInput, ParserOutput
from backend.flask.models.app_templated_models import Render, ResultPageModel
from backend.renderers.base_renderer import RendererOutputType
from backend.services import parser_comparison_service, parserservice
from backend.services.parser_comparison_service import ParserComparisonService
from backend.services.pipeline_manager_service import get_plugin_information_model
from . import app
from . import parser_service, pipeline_manager
from . import LoginForm, TextOrFileForm

from ...commons.t2t_logging import log_class_methods, log_decorated, log_info

from flask import render_template, flash, redirect, url_for, request

import os


@app.route('/parsers')
def get_parsers():
    return parser_service.get_parser_names()


@app.route('/get_and_parse', methods=['GET', 'POST'])
def get_and_parse():
    text_or_file_form = TextOrFileForm()
    text_or_file_form.parser_selection.choices = [(p,p) for p in parser_service.get_parser_names()]

    if text_or_file_form.validate_on_submit():
        if not text_or_file_form.text_area.data and not text_or_file_form.file_upload.data:
            flash("Please provide either text or a file.", "error")
            return redirect(url_for("get_and_parse"))
        elif text_or_file_form.text_area.data and text_or_file_form.file_upload.data:
            flash("Please provide only one: either text or a file.", "error")
            return redirect(url_for("get_and_parse"))



        selected_parser = "ERROR_NOT_SET"
        if text_or_file_form.text_area.data:
            input_text = text_or_file_form.text_area.data
        else:
            file = text_or_file_form.file_upload.data
            input_text = file.read().decode("utf-8")

        selected_mode = request.form.get("select_type")

        # TODO extract modes somewhere and clean up the controllers
        if selected_mode == "compare":
            selected_parsers = request.form.getlist('parser_selection')
            return compare_parsers(input_text, selected_parsers)
        elif selected_mode == "generate":
            selected_parser = text_or_file_form.parser_selection.data
            return parse(input_text, selected_parser, request)


    return render_template('input.html', form=text_or_file_form, plugin_info = get_plugin_information_model(pipeline_manager))


def parse(input_text, parser, request):
    disabled_plugins = request.form.getlist("disabled_plugins")
    
    if disabled_plugins:
        pipeline_manager._disabled_keys = disabled_plugins

    result_model : ResultPageModel = pipeline_manager.run_pipeline_result_page_model(input_text, parser)
    return render_template('results.html', results=result_model)


def compare_parsers(input_text, parsers):
    # For now, running this without the pipeline manager as I'm not sure whether I want
    # plugins affected parser stats

    parser_comparison_service = ParserComparisonService(parser_service)
    parser_comparison_service.parse_and_compare(parsers, input_text)
    result_model: ResultPageModel = parser_comparison_service.build_result_page_model()
    return render_template('compare_parsers.html', results=result_model)


""" @app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            login_form.username.data, login_form.remember_me.data))
        return redirect(url_for("index"))
    return render_template('login.html', title='Sign In', form=login_form) """


@app.route('/')
@app.route('/index')
def index():
    #return render_template('index.html')
    return redirect(url_for("get_and_parse"))