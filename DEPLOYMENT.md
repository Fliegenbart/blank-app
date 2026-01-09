# 🚀 Deployment Guide - Barrierefreiheits-Tools

## Empfohlene Deployment-Optionen für Streamlit Apps

### ⭐ Option 1: Streamlit Community Cloud (Empfohlen & Kostenlos)

**Streamlit Community Cloud** ist die beste und einfachste Option für Streamlit-Apps.

#### Schritte:

1. **Pushen Sie Ihren Code zu GitHub**
   ```bash
   git push origin claude/accessibility-tools-website-EK47X
   ```

2. **Gehen Sie zu [share.streamlit.io](https://share.streamlit.io)**

3. **Melden Sie sich mit GitHub an**

4. **Klicken Sie auf "New app"**

5. **Konfigurieren Sie Ihre App:**
   - Repository: `Fliegenbart/blank-app`
   - Branch: `claude/accessibility-tools-website-EK47X` (oder `main`)
   - Main file path: `streamlit_app.py`

6. **Klicken Sie auf "Deploy"**

Die App wird automatisch deployed! Streamlit Cloud liest automatisch:
- `requirements.txt` für Python-Pakete
- `packages.txt` für System-Abhängigkeiten
- `.streamlit/config.toml` für Streamlit-Konfiguration

**URL:** Sie erhalten eine öffentliche URL wie `https://[app-name].streamlit.app`

---

### 🐳 Option 2: Docker + Cloud Run / Heroku / Railway

Falls Sie Docker bevorzugen, können Sie einen Container erstellen:

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code kopieren
COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Deployment:**
- **Google Cloud Run:** `gcloud run deploy`
- **Heroku:** `heroku container:push web && heroku container:release web`
- **Railway:** Einfach GitHub Repository verbinden

---

### 🔧 Option 3: VPS (DigitalOcean, AWS EC2, etc.)

Für mehr Kontrolle können Sie einen VPS verwenden:

```bash
# Auf dem Server
git clone https://github.com/Fliegenbart/blank-app.git
cd blank-app
git checkout claude/accessibility-tools-website-EK47X

# Abhängigkeiten installieren
sudo apt-get update
sudo apt-get install -y python3-pip poppler-utils
pip3 install -r requirements.txt

# Mit PM2 oder systemd als Daemon laufen lassen
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

---

## ❌ Warum Vercel NICHT funktioniert

**Vercel ist für Streamlit nicht geeignet**, weil:
- Vercel ist für serverlose Funktionen (Lambda) optimiert
- Streamlit benötigt einen dauerhaft laufenden WebSocket-Server
- Vercel hat Timeout-Limits (10s für Hobby, 60s für Pro)
- Streamlit-Sessions würden bei jedem Request neu starten

**Alternativen zu Vercel für Python-Webapps:**
- ✅ Streamlit Community Cloud (für Streamlit)
- ✅ Railway (für alle Python-Apps)
- ✅ Render (für alle Python-Apps)
- ✅ Fly.io (für Containerized Apps)
- ❌ Vercel (nur für Next.js, Static Sites, Serverless Functions)

---

## 📋 Deployment-Checkliste

Vor dem Deployment sicherstellen:

- [ ] `requirements.txt` enthält alle Python-Pakete
- [ ] `packages.txt` enthält System-Abhängigkeiten (falls nötig)
- [ ] `.streamlit/config.toml` ist konfiguriert
- [ ] Code ist zu GitHub gepusht
- [ ] Keine hardcodierten Secrets (nutzen Sie Streamlit Secrets)
- [ ] App läuft lokal ohne Fehler

---

## 🔐 Secrets Management (Optional)

Falls Sie API-Keys benötigen:

1. Erstellen Sie `.streamlit/secrets.toml` (lokal, nicht in Git)
2. In Streamlit Cloud: Settings → Secrets
3. Zugriff im Code: `st.secrets["api_key"]`

---

## 📊 Performance-Tipps

- Verwenden Sie `@st.cache_data` für teure Berechnungen
- Optimieren Sie Datei-Uploads (max. Größe setzen)
- Nutzen Sie `st.spinner()` für lange Operationen
- Erwägen Sie Redis für Session-State in Produktion

---

## 🆘 Troubleshooting

### App startet nicht
- Überprüfen Sie Logs in Streamlit Cloud
- Testen Sie lokal: `streamlit run streamlit_app.py`
- Prüfen Sie, ob alle Dependencies in `requirements.txt` sind

### Fehler bei Package-Installation
- System-Pakete gehören in `packages.txt`, nicht `requirements.txt`
- Python-Module aus Standardbibliothek (wie `colorsys`) NICHT in `requirements.txt`

### Memory-Fehler
- Reduzieren Sie Bild-/Dateigrößen
- Verwenden Sie Streaming für große Dateien
- Upgraden Sie auf Streamlit Cloud Pro (mehr RAM)

---

**Viel Erfolg beim Deployment! 🚀**
