from backend.commons.parser_commons import ParserInput, ParserOutput
from backend.services import parserservice
from . import app
from . import parser_service
from . import LoginForm, TextOrFileForm

from ...commons.t2t_logging import log_info

from flask import render_template, flash, redirect, url_for, request

import os

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
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/parsers')
def get_parsers():
    return parser_service.get_parser_names()


@app.route('/input', methods=['GET', 'POST'])
def get_and_parse():
    text_or_file_form = TextOrFileForm()
    text_or_file_form.parser_selection.choices = [(p,p) for p in parser_service.get_parser_names()]

    if text_or_file_form.validate_on_submit():
        # Ensure only one input is provided
        if not text_or_file_form.text_area.data and not text_or_file_form.file_upload.data:
            flash("Please provide either text or a file.", "error")
        elif text_or_file_form.text_area.data and text_or_file_form.file_upload.data:
            flash("Please provide only one: either text or a file.", "error")
        else:
            selected_parser = "ERROR_NOT_SET"
            if text_or_file_form.text_area.data:
                # Handle text area input
                input_text = text_or_file_form.text_area.data
            else:
                # Handle file upload
                file = text_or_file_form.file_upload.data

                log_info(file) # ? 

                # filename = secure_filename(file.filename)  werkzeug util, probably not necessary at this point
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file)
                file.save(filepath)
                with open(filepath, 'r') as f:
                    input_text = f.read()
                
            selected_parser = text_or_file_form.parser_selection.data
            print("Parser selected from FE", selected_parser)
            return redirect(url_for('parse', input_text=input_text, parser=selected_parser))
    return render_template('input.html', form=text_or_file_form)


@app.route('/parse')
def parse():
    input_text = str(request.args.get('input_text'))
    parser_input: ParserInput = ParserInput(input_text)

    output: ParserOutput = parser_service.parse_with_selected(parser_input, str(request.args.get("parser")))
    current_page = output.get_current_page()

    return f"Processed text: {current_page[0]}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            login_form.username.data, login_form.remember_me.data))
        return redirect(url_for("index"))
    return render_template('login.html', title='Sign In', form=login_form)