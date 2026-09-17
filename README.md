# NVIDIA AI Chat

Eine kleine App (Python + FastAPI), die Fragen entgegennimmt, sie über die
[NVIDIA API](https://build.nvidia.com) an ein LLM schickt und die Antwort anzeigt.

## Features

- FastAPI-Backend mit Endpunkt `POST /api/chat`
- Einfaches Web-Frontend unter `/` (HTML/JS, kein Build-Tool nötig)
- Unterstützt Gesprächsverlauf (History) und Modellwahl
- `.env`-basierte Konfiguration des API-Keys

## Setup

```bash
# 1. Virtuelle Umgebung anlegen
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. .env Datei anlegen
cp .env.example .env
# dann NVIDIA_API_KEY in .env eintragen (siehe unten, wo man den Key bekommt)

# 4. Server starten
uvicorn app.main:app --reload
```

Danach im Browser öffnen: http://127.0.0.1:8000

## NVIDIA API-Key bekommen

1. Auf https://build.nvidia.com registrieren/einloggen.
2. Ein Modell auswählen (z. B. Llama 3.1) und "Get API Key" klicken.
3. Den Key (beginnt mit `nvapi-...`) in die `.env` Datei eintragen.

## API

### `POST /api/chat`

Request-Body:
```json
{
  "question": "Was ist die Hauptstadt von Frankreich?",
  "model": "meta/llama-3.1-8b-instruct",
  "history": [
    {"role": "user", "content": "Hallo"},
    {"role": "assistant", "content": "Hallo! Wie kann ich helfen?"}
  ],
  "temperature": 0.5,
  "max_tokens": 1024
}
```

Nur `question` ist erforderlich. Response:
```json
{
  "answer": "Die Hauptstadt von Frankreich ist Paris.",
  "model": "meta/llama-3.1-8b-instruct"
}
```

### `GET /api/health`

Prüft, ob der Server läuft und ein API-Key konfiguriert ist.

## Andere Modelle verwenden

NVIDIA bietet viele Modelle über denselben OpenAI-kompatiblen Endpunkt an
(z. B. `meta/llama-3.1-70b-instruct`, `mistralai/mixtral-8x7b-instruct-v0.1`,
`google/gemma-2-27b-it`). Einfach das gewünschte Modell im Request-Body als
`model` mitschicken, oder `NVIDIA_MODEL` in der `.env` als neuen Standard
setzen.

## Projektstruktur

```
nvidia-ai-chat/
├── app/
│   ├── main.py          # FastAPI-Anwendung
│   └── static/
│       └── index.html   # Frontend
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Lizenz

MIT
