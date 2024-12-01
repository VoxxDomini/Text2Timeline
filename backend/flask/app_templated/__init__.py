from flask import Flask
from .config import Config
from ...services.parserservice import ParserService
from ...commons.t2t_logging import initialize_logging
from .forms.forms import LoginForm, TextOrFileForm

import threading


initialize_logging()

parser_service = ParserService()
parser_service.load_default_parsers()
parser_service.init_parsers_async()
parser_service.confirm_parsers_loaded()
            

app = Flask(__name__)
app.config.from_object(Config)

from . import routes