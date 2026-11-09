FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY naviqra ./naviqra
RUN pip install --no-cache-dir ".[postgres]"
ENV NAVIQRA_ENV=production NAVIQRA_DOCS=false NAVIQRA_MAX_REQUEST_BYTES=1048576
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import os,urllib.request; host=os.environ.get('NAVIQRA_ALLOWED_HOSTS','').split(',')[0].strip(); req=urllib.request.Request('http://127.0.0.1:8000/health',headers={'Host':host}); urllib.request.urlopen(req,timeout=3)"
CMD ["uvicorn", "naviqra.api:app", "--host", "0.0.0.0", "--port", "8000"]
