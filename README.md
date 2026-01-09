# ♿ Barrierefreiheits-Tools Website

Eine umfassende Web-Plattform mit verschiedenen Online-Tools zur Erstellung und Prüfung barrierefreier digitaler Inhalte gemäß den **Web Content Accessibility Guidelines (WCAG 2.1)**.

## 📋 Übersicht

Diese Website bietet eine Sammlung von Tools, die dabei helfen, digitale Inhalte barrierefrei zu gestalten und bestehende Inhalte auf Barrierefreiheit zu prüfen. Alle Tools sind kostenlos und erfordern keine Registrierung.

## 🛠️ Verfügbare Tools

### 📊 PowerPoint zu barrierefreiem PDF
- Konvertiert PowerPoint-Präsentationen (.pptx) in barrierefreie PDF-Dokumente
- Erhält die Textstruktur und logische Lesereihenfolge
- Extrahiert und behält Alternativtexte für Bilder bei
- Erstellt optional ein Inhaltsverzeichnis
- Fügt Barrierefreiheits-Metadaten hinzu
- Unterstützt A4 und Letter Format

**Funktionen:**
- Strukturierte Überschriften
- Screenreader-kompatible Textebenen
- Bildextraktion mit Alternativtexten
- Anpassbare Konvertierungsoptionen

### 🎨 Farbkontrast-Checker
- Überprüft Farbkombinationen auf WCAG-Konformität
- Berechnet präzise Kontrastverhältnisse
- Bewertet nach AA und AAA Standards
- Live-Vorschau von Text mit den gewählten Farben
- Gibt konkrete Empfehlungen zur Verbesserung

**WCAG-Standards:**
- **Level AA:** 4.5:1 für normalen Text, 3:1 für großen Text
- **Level AAA:** 7:1 für normalen Text, 4.5:1 für großen Text

### 🖼️ Alt-Text Generator
- Hilft bei der Erstellung aussagekräftiger Alternativtexte für Bilder
- Zeigt Best Practices und Richtlinien an
- Bietet kontextspezifische Hilfestellungen
- Zeichenzähler mit Empfehlungen
- Bewertung der Alt-Text-Qualität
- Unterstützt verschiedene Bildtypen (informativ, dekorativ, funktional, komplex)

**Features:**
- Bilddetails-Anzeige (Format, Größe, Modus)
- HTML-Code-Generierung
- Automatische Qualitätsprüfung

### 📄 PDF Barrierefreiheitsprüfer
- Analysiert PDF-Dokumente auf Barrierefreiheit
- Extrahiert und prüft Text auf Screenreader-Kompatibilität
- Untersucht Metadaten und Dokumentstruktur
- Identifiziert Bilder ohne Alternativtexte
- Erstellt detaillierte Bewertungen mit Score
- Gibt spezifische Verbesserungsempfehlungen

**Geprüfte Aspekte:**
- Textextraktion
- Metadaten (Titel, Autor, Sprache)
- Bildanalyse
- Dokumentstruktur

### 🔊 Text-zu-Sprache Konverter
- Konvertiert Text in natürlich klingende Audiodateien
- Unterstützt 10 verschiedene Sprachen
- Anpassbare Sprechgeschwindigkeit
- MP3-Download-Funktion
- Integrierter Audio-Player
- Geschätzte Audiozeit-Berechnung

**Unterstützte Sprachen:**
- Deutsch, Englisch, Französisch, Spanisch, Italienisch
- Niederländisch, Polnisch, Portugiesisch, Russisch, Türkisch

**Anwendungsfälle:**
- Hörbuch-Versionen von Dokumenten
- Audiodeskriptionen
- Barrierefreie Web-Inhalte
- Lernmaterialien

## 🚀 Installation und Verwendung

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Installation

1. Repository klonen:
```bash
git clone <repository-url>
cd blank-app
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

### Anwendung starten

```bash
streamlit run streamlit_app.py
```

Die Website wird automatisch im Browser unter `http://localhost:8501` geöffnet.

## 🌐 Online Deployment

### Empfohlen: Streamlit Community Cloud (Kostenlos)

Die einfachste Methode, diese App online zu deployen:

1. **Pushen Sie den Code zu GitHub** (bereits erledigt ✓)
2. **Gehen Sie zu [share.streamlit.io](https://share.streamlit.io)**
3. **Melden Sie sich mit GitHub an**
4. **Klicken Sie auf "New app" und wählen Sie:**
   - Repository: `Fliegenbart/blank-app`
   - Branch: `claude/accessibility-tools-website-EK47X` oder `main`
   - Main file: `streamlit_app.py`
5. **Klicken Sie auf "Deploy"**

Ihre App wird in wenigen Minuten unter einer öffentlichen URL verfügbar sein!

**⚠️ Hinweis:** Vercel wird NICHT unterstützt, da Streamlit einen dauerhaft laufenden Server benötigt. Verwenden Sie Streamlit Community Cloud, Railway oder Render.

📖 Ausführliche Deployment-Anleitung: Siehe [DEPLOYMENT.md](DEPLOYMENT.md)

## 📦 Verwendete Technologien

- **Streamlit** - Web-Framework für die Benutzeroberfläche
- **python-pptx** - PowerPoint-Datei-Verarbeitung
- **ReportLab** - PDF-Generierung
- **PyMuPDF (fitz)** - PDF-Analyse und -Extraktion
- **Pillow (PIL)** - Bildverarbeitung
- **gTTS (Google Text-to-Speech)** - Text-zu-Sprache-Konvertierung
- **pypdf** - PDF-Manipulation

## 📖 WCAG 2.1 Richtlinien

Diese Tools basieren auf den **Web Content Accessibility Guidelines (WCAG) 2.1**, die internationale Standards für barrierefreie Web-Inhalte definieren.

**Konformitätsstufen:**
- **Level A:** Minimale Barrierefreiheit
- **Level AA:** Akzeptable Barrierefreiheit (empfohlen für die meisten Websites)
- **Level AAA:** Optimale Barrierefreiheit

Weitere Informationen: [W3C WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)

## 🎯 Funktionsweise

### PPT zu PDF Konverter
1. PowerPoint-Datei hochladen (.pptx)
2. Konvertierungsoptionen auswählen (Bilder, Metadaten, Format, TOC)
3. Auf "Konvertieren" klicken
4. Barrierefreies PDF herunterladen

### Farbkontrast-Checker
1. Vordergrundfarbe (Text) wählen
2. Hintergrundfarbe wählen
3. Kontrastverhältnis wird automatisch berechnet
4. Ergebnis nach WCAG AA/AAA prüfen
5. Empfehlungen befolgen

### Alt-Text Generator
1. Bild hochladen
2. Bildtyp auswählen (informativ, dekorativ, etc.)
3. Beschreibung eingeben
4. Qualität überprüfen
5. HTML-Code kopieren

### PDF Prüfer
1. PDF-Dokument hochladen
2. Auf "Prüfen" klicken
3. Analyseergebnisse anzeigen
4. Empfehlungen umsetzen

### Text-zu-Sprache
1. Text eingeben oder einfügen
2. Sprache auswählen
3. Optional: Langsame Geschwindigkeit aktivieren
4. Audio generieren
5. Anhören und/oder herunterladen

## 🌐 Barrierefreiheit der Website selbst

Diese Website wurde mit Fokus auf Barrierefreiheit entwickelt:
- Semantisches HTML
- Ausreichende Farbkontraste
- Klare Navigation
- Verständliche Beschriftungen
- Responsive Design
- Tastaturnavigation

## 🤝 Beitragen

Verbesserungsvorschläge und Beiträge sind willkommen! Bitte erstellen Sie ein Issue oder einen Pull Request.

## 📄 Lizenz

Siehe [LICENSE](LICENSE) Datei für Details.

## 💡 Hinweise

- Alle Verarbeitungen finden lokal statt - keine Daten werden an externe Server gesendet
- Die Tools sind als Hilfsmittel gedacht und ersetzen keine manuelle Barrierefreiheitsprüfung
- Für vollständige WCAG-Konformität sollten zusätzliche Tests durchgeführt werden

## 🔗 Weiterführende Ressourcen

- [WCAG 2.1 Richtlinien](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM - Web Accessibility In Mind](https://webaim.org/)
- [A11Y Project](https://www.a11yproject.com/)
- [MDN Web Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

---

**Entwickelt mit ❤️ für eine zugänglichere digitale Welt**
