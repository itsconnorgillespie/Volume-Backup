FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade -r requirements.txt

FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /usr/local /usr/local
COPY src ./src

RUN adduser \
    --no-create-home \
    --disabled-password \
    --shell /bin/bash \
    --uid 1000 \
    --quiet \
    runtime
USER runtime

ENTRYPOINT ["python", "-m", "src.main"]
