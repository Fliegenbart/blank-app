FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements-server.txt ./
ARG INSTALL_MODELS=1
RUN pip install --no-cache-dir -r $([ "$INSTALL_MODELS" = "1" ] && echo requirements-server.txt || echo requirements.txt)

COPY server ./server
COPY static ./static
COPY glossary.csv ./

EXPOSE 8026
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8026"]
