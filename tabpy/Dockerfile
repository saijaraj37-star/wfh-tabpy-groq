FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir tabpy requests

WORKDIR /app
COPY tabpy.conf entrypoint.sh deploy_cpu.py /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 9004
CMD ["/app/entrypoint.sh"]