FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for tiktoken
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD uvicorn api_app:app --host 0.0.0.0 --port ${PORT:-8000}
