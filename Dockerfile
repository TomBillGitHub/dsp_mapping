FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Poetry
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /opt/app

ARG PORT=8080
ENV PORT=$PORT

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Create working directory
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

WORKDIR /opt/app

EXPOSE 8080

ENV POST_MODE=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]