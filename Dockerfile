FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY socks5_bench/ socks5_bench/
RUN pip install --no-cache-dir .

RUN useradd --create-home appuser
USER appuser

ENTRYPOINT ["socks5-bench"]
