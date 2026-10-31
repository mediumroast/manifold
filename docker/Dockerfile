# The build context is the repository root:  docker build -f docker/Dockerfile .
FROM python:3.12-slim

ARG SERVER_DIR=server

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    CONTAINER_WIKI_ROOT=/workspace \
    MANIFOLD_HOST=0.0.0.0 \
    PORT=8686

# git: the server commits wiki changes.  curl: the health check.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin manifold

WORKDIR /app

COPY ${SERVER_DIR}/requirements.txt ${SERVER_DIR}/requirements.lock ./
RUN pip install -r requirements.txt -c requirements.lock

# Server code, the core assets, and the agent bundles (the bundle ZIPs are built below).
COPY ${SERVER_DIR}/ .
COPY assets/ ./assets/
COPY bundles/ ./bundles/
RUN set -e; \
    for build in bundles/*/tools/build.py; do \
        [ -f "$build" ] || continue; \
        bundle="$(dirname "$(dirname "$build")")"; \
        (cd "$bundle" && python tools/build.py --out dist); \
    done

# The instance repository is mounted here.  The server writes only inside it.
VOLUME ["/workspace"]
USER manifold

# Inside the container the server listens on all interfaces; the compose file
# publishes the port on the host's loopback address only.
EXPOSE 8686

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

CMD ["sh", "-c", "exec python -m uvicorn server:asgi_app --host \"$MANIFOLD_HOST\" --port \"$PORT\""]
