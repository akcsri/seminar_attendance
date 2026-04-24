# syntax=docker/dockerfile:1
FROM python:3.11-slim

# ---- System deps ----
# build-essential は psycopg2-binary には不要だが、他Cライブラリが要求されても落ちないよう最小限入れておく
# libpq5 は psycopg2-binary が動的にロードする libpq
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Tokyo

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        tzdata \
        libpq5 \
        ca-certificates \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- Python deps ----
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---- App code ----
COPY . .

# Flyは 8080 をデフォルトで期待
ENV PORT=8080
EXPOSE 8080

# gunicorn + Flask-APScheduler を安全に動かすため、必ず workers=1
# threads を増やして同時リクエストに対応
# preload_app しないことで scheduler が 1 度だけ起動する
CMD ["sh", "-c", "gunicorn -w 1 --threads 4 -b 0.0.0.0:${PORT} --timeout 120 --access-logfile - --error-logfile - wsgi:app"]
