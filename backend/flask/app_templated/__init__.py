from flask import Flask
import matplotlib
from .config import Config
from ...services.parserservice import ParserService
from ...services.renderservice import RendererService
from ...commons.t2t_logging import initialize_logging
from .forms.forms import LoginForm, TextOrFileForm
from ..services.result_builder import ResultBuilder

import matplotlib.pyplot as plt

# searchable comment tech INIT ENTRYPOINT

# Move this to somewhere else, rc params can be modified from anywhere
matplotlib.use('agg')
plt.rcParams['axes.facecolor'] = '#adadad'
plt.rcParams['figure.facecolor'] = '#adadad'

initialize_logging()

'''
Parser service loads model files from disk
having it behave as once-per-request would make it much slower
do barebones in-process worker queue to make it REST viable
still sucks but not enough ram to run multiple instances 
'''
parser_service = ParserService()
# parser_service.load_default_parsers()
#parser_service.confirm_parsers_loaded()

'''
These don't actually need to be here but they're getting
dependency injected anyway just make sure no new state per request
'''
render_service = RendererService()
result_builder = ResultBuilder()

app = Flask(__name__)
app.config.from_object(Config)

from . import routes