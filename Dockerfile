FROM python:3.12-alpine AS builder

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install .

FROM python:3.12-alpine AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk upgrade --no-cache \
    && python -m pip uninstall -y pip \
    && rm -rf /usr/local/lib/python3.12/ensurepip

COPY --from=builder /install /usr/local
COPY src ./src

RUN addgroup -S runtime && adduser -S -G runtime runtime
USER runtime

ENTRYPOINT ["python", "-m", "src.main"]
