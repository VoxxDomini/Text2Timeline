from math import log
from backend.commons.parser_commons import ParserInput, ParserOutput
from backend.flask.models.app_templated_models import Render, ResultPageModel
from backend.renderers.base_renderer import RendererOutputType
from backend.services import parserservice
from . import app
from . import parser_service, render_service, result_builder
from . import LoginForm, TextOrFileForm

from ...commons.t2t_logging import log_class_methods, log_info

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
        elif text_or_file_form.text_area.data and text_or_file_form.file_upload.data:
            flash("Please provide only one: either text or a file.", "error")
        else:
            selected_parser = "ERROR_NOT_SET"
            if text_or_file_form.text_area.data:
                # Text area input
                input_text = text_or_file_form.text_area.data
            else:
                # Uploaded input
                file = text_or_file_form.file_upload.data

                # TODO add option to keep user uploads
                # Example:
                """
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file)
                file.save(filepath)

                with open(filepath, 'r') as f:
                    input_text = f.read()

                """
                input_text = file.read().decode("utf-8")
                
            selected_parser = text_or_file_form.parser_selection.data
            return parse(input_text, selected_parser)
    return render_template('input.html', form=text_or_file_form)


def parse(input_text, parser):
    # TODO move all this logic into Result Builder

    parser_input: ParserInput = ParserInput(input_text)
    output: ParserOutput = parser_service.parse_with_selected(parser_input, parser)

    # render = render_service.render_with_selected("MPL", output)
    render_list = render_service.render_with_all(output)

    result_model : ResultPageModel = result_builder.build(output, render_list)

    return render_template('results.html', results=result_model)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            login_form.username.data, login_form.remember_me.data))
        return redirect(url_for("index"))
    return render_template('login.html', title='Sign In', form=login_form)


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    # return render_template('index.html', title='Home', user=user, posts=posts)
    return redirect(url_for("get_and_parse"))