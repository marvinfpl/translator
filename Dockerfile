FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Préchargement modèles
RUN python -c "from transformers import pipeline; \
pipeline('automatic-speech-recognition', model='openai/whisper-base'); \
pipeline('text-to-speech', model='facebook/mms-tts-fra')"

COPY . .

CMD ["python", "main.py"]