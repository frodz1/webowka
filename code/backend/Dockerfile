FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/frodz1/webowka"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

# Łatki bezpieczeństwa systemu, których obraz bazowy jeszcze nie ma (wykrywa je Trivy).
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh && useradd --system --no-create-home app

# Proces aplikacji nie działa jako root.
USER app

EXPOSE 5000
ENTRYPOINT ["./entrypoint.sh"]
