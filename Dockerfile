FROM python:3.11

WORKDIR /src

RUN pip install pipenv
COPY .env .env
COPY ./Pipfile ./Pipfile
COPY ./Pipfile.lock ./Pipfile.lock
COPY ./make-news-letter.py ./make-news-letter.py
RUN pipenv install --dev --system --deploy

CMD ["python","./make-news-letter.py"]