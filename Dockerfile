FROM python:3.9.5-buster

RUN pip install poetry==1.8.3

ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY README.md ./

# experiment with order to change cahcing to not redownload

# RUN poetry install --no-dev --no-root && rm -rf $POETRY_CACHE_DIR
RUN poetry install --without dev

# EXPOSE 5000
RUN poetry run python -c "import nltk; nltk.download('punkt')"
RUN poetry run python -m spacy download en_core_web_sm

COPY text2timeline.py ./
COPY resources ./resources
COPY frontend ./frontend
COPY backend ./backend

ENV NAME Text2Timeline

ENTRYPOINT ["poetry", "run", "python", "-m", "text2timeline"]

