FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
COPY pyproject.toml ./
RUN poetry install --no-dev --no-root

COPY . .
RUN mkdir -p logs media staticfiles

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]