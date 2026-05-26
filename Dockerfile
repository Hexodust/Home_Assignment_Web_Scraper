# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

LABEL maintainer="me@salimane.com" \
      vendor="salimane" \
      name="salimane/flask-mvc" \
      description="Python boilerplate application following MVC pattern using Flask." \
      com.salimane.component.name="flask-mvc" \
      com.salimane.component.distribution-scope="public" \
      com.salimane.component.changelog-url="https://github.com/salimane/flask-mvc/releases" \
      com.salimane.component.url="https://github.com/salimane/flask-mvc"

ARG BUILD_DATE
ARG VCS_REF
ARG VCS_REF_MSG
ARG VCS_URL
ARG VERSION

LABEL com.salimane.component.build-date="$BUILD_DATE" \
      com.salimane.component.vcs-url="$VCS_URL" \
      com.salimane.component.vcs-ref="$VCS_REF" \
      com.salimane.component.vcs-ref-msg="$VCS_REF_MSG" \
      com.salimane.component.version="$VERSION"

ENV LANG=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SECRET_KEY="3e8220bf2c657de2b5dfc2d07663db36ad4088c1407f94ee014fbd0c715815aa"

# System packages — single layer, BuildKit cache mounts keep apt downloads across builds.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc \
      build-essential \
      libffi-dev \
      libssl-dev \
      libpq-dev \
      cron

WORKDIR /opt/flask

# Python deps — only re-runs when requirements.txt changes; pip wheel cache persists across builds.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -U pip && \
    pip install -r requirements.txt

# Playwright browsers + their system deps — only re-runs when requirements.txt changes.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    playwright install --with-deps chromium

# Copy application source (this is the only layer that rebuilds on a code change).
COPY . .

COPY cronjob /etc/cron.d/scraper-cron
RUN chmod 0644 /etc/cron.d/scraper-cron && touch /var/log/cron_scraper.log

EXPOSE 16000

CMD ["sh", "-c", "env > /etc/environment && cron && gunicorn runserver:app --bind 0.0.0.0:16000 --workers 4 --threads 2 --worker-class sync"]