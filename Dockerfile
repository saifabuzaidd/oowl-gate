FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY oowl/ ./oowl/
COPY app/ ./app/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["python3", "app/run_project.py"]
