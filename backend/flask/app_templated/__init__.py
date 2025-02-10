from flask import Flask
import matplotlib

from backend.services.pipeline_manager_service import PipelineManagerService
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
plt.rcParams['axes.facecolor'] = '#e8e8e8'
plt.rcParams['figure.facecolor'] = '#e8e8e8'

initialize_logging()

'''
Parser service loads model files from disk
having it behave as once-per-request would make it much slower
do barebones in-process worker queue to make it REST viable
still sucks but not enough ram to run multiple instances 
'''

pipeline_manager: PipelineManagerService = PipelineManagerService()
parser_service = pipeline_manager.parser_service

app = Flask(__name__)
app.config.from_object(Config)

from . import routes