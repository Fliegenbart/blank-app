import streamlit as st
import io
from pptx import Presentation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PIL import Image
import colorsys
from gtts import gTTS
import tempfile
import os
import fitz  # PyMuPDF
import re
from html.parser import HTMLParser
from docx import Document
from docx.shared import Inches, Pt
import json

# Seitenkonfiguration
st.set_page_config(
    page_title="Barrierefreiheits-Tools",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für bessere Barrierefreiheit
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tool-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Hauptüberschrift
st.markdown('<h1 class="main-header">♿ Barrierefreiheits-Tools</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #555;">Werkzeuge zur Erstellung und Prüfung barrierefreier Inhalte</p>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
tool_option = st.sidebar.radio(
    "Wählen Sie ein Tool:",
    ["Übersicht", "PPT zu PDF", "Word zu PDF", "Farbkontrast-Checker", "Alt-Text Generator",
     "PDF Prüfer", "Text-zu-Sprache", "HTML Checker", "Leichte Sprache", "ARIA Helper", "Untertitel Generator"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Über diese Tools")
st.sidebar.info("Diese Website bietet verschiedene Tools zur Erstellung und Prüfung barrierefreier Inhalte gemäß WCAG 2.1 Richtlinien.")

# Übersicht
if tool_option == "Übersicht":
    st.markdown('<h2 class="tool-header">Willkommen bei den Barrierefreiheits-Tools</h2>', unsafe_allow_html=True)

    st.markdown("""
    Diese Plattform bietet Ihnen eine umfassende Sammlung von Online-Tools zur Verbesserung
    der digitalen Barrierefreiheit. Alle Tools sind darauf ausgelegt, Inhalte gemäß den
    **Web Content Accessibility Guidelines (WCAG 2.1)** zu erstellen oder zu prüfen.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 PPT zu barrierefreiem PDF")
        st.markdown("""
        Konvertieren Sie PowerPoint-Präsentationen in vollständig barrierefreie PDF-Dokumente:
        - Erhaltung der Textstruktur
        - Alternativtexte für Bilder
        - Lesezeichen und Navigation
        - Tagged PDF für Screenreader
        """)

        st.markdown("### 🎨 Farbkontrast-Checker")
        st.markdown("""
        Überprüfen Sie Farbkombinationen auf WCAG-Konformität:
        - AA und AAA Level Bewertung
        - Kontrastverhältnis-Berechnung
        - Verbesserungsvorschläge
        """)

        st.markdown("### 🖼️ Alt-Text Generator")
        st.markdown("""
        Erstellen Sie aussagekräftige Alternativtexte für Bilder:
        - Beschreibungen für Screenreader
        - Kontextbezogene Texte
        - Best Practices Empfehlungen
        """)

    with col2:
        st.markdown("### 📄 PDF Barrierefreiheitsprüfer")
        st.markdown("""
        Analysieren Sie PDF-Dokumente auf Barrierefreiheit:
        - Struktur-Prüfung
        - Textextraktion
        - Metadaten-Analyse
        - Verbesserungsvorschläge
        """)

        st.markdown("### 🔊 Text-zu-Sprache")
        st.markdown("""
        Konvertieren Sie Text in Audiodateien:
        - Mehrere Sprachen
        - Natürliche Stimmen
        - MP3-Download
        - Ideal für Hörbuch-Versionen
        """)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 📝 Word zu barrierefreiem PDF")
        st.markdown("""
        Konvertieren Sie Word-Dokumente in barrierefreie PDFs:
        - Strukturierte Überschriften
        - Tabellen-Extraktion
        - Listen-Formatierung
        - Metadaten-Übernahme
        """)

        st.markdown("### 🌐 HTML Barrierefreiheits-Checker")
        st.markdown("""
        Prüfen Sie HTML-Code auf Barrierefreiheit:
        - Alt-Text Prüfung
        - ARIA-Attribute Check
        - Semantische Struktur
        - WCAG-Konformität
        """)

        st.markdown("### 📖 Leichte Sprache")
        st.markdown("""
        Texte in Leichte Sprache umwandeln:
        - Satzlängen-Analyse
        - Wort-Komplexität prüfen
        - Vereinfachungsvorschläge
        - Lesbarkeitsindex
        """)

    with col4:
        st.markdown("### ♿ ARIA Helper")
        st.markdown("""
        Hilfe bei ARIA-Attributen:
        - Rollen-Übersicht
        - Attribut-Generator
        - Best Practices
        - Code-Beispiele
        """)

        st.markdown("### 🎬 Untertitel Generator")
        st.markdown("""
        Untertitel und Transkripte erstellen:
        - SRT-Format Export
        - VTT-Format Export
        - Zeitstempel-Editor
        - Multi-Sprachen
        """)

    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    **💡 Tipp:** Wählen Sie ein Tool aus der Seitenleiste, um zu beginnen.
    Alle Tools sind kostenlos und erfordern keine Registrierung.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# PPT zu PDF Konverter
elif tool_option == "PPT zu PDF":
    st.markdown('<h2 class="tool-header">📊 PowerPoint zu barrierefreiem PDF</h2>', unsafe_allow_html=True)

    st.markdown("""
    Dieses Tool konvertiert Ihre PowerPoint-Präsentationen in barrierefreie PDF-Dokumente.
    Das resultierende PDF enthält:
    - Strukturierte Überschriften
    - Lesbaren Text für Screenreader
    - Alternativtexte für Bilder (wenn vorhanden)
    - Logische Lesereihenfolge
    """)

    uploaded_file = st.file_uploader("Laden Sie eine PowerPoint-Datei hoch", type=['pptx'])

    if uploaded_file is not None:
        st.success(f"Datei '{uploaded_file.name}' erfolgreich hochgeladen!")

        # Optionen
        st.markdown("### Konvertierungsoptionen")
        col1, col2 = st.columns(2)
        with col1:
            include_images = st.checkbox("Bilder einbeziehen", value=True)
            add_metadata = st.checkbox("Barrierefreiheits-Metadaten hinzufügen", value=True)
        with col2:
            page_size = st.selectbox("Seitengröße", ["A4", "Letter"])
            add_toc = st.checkbox("Inhaltsverzeichnis erstellen", value=True)

        if st.button("In barrierefreies PDF konvertieren", type="primary"):
            with st.spinner("Konvertierung läuft..."):
                try:
                    # PowerPoint laden
                    prs = Presentation(uploaded_file)

                    # PDF erstellen
                    pdf_buffer = io.BytesIO()
                    pdf_size = A4 if page_size == "A4" else letter
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=pdf_size)

                    # Styles
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle(
                        'CustomTitle',
                        parent=styles['Heading1'],
                        fontSize=24,
                        textColor=colors.HexColor('#1f77b4'),
                        spaceAfter=30,
                        alignment=TA_CENTER
                    )
                    heading_style = ParagraphStyle(
                        'CustomHeading',
                        parent=styles['Heading2'],
                        fontSize=16,
                        textColor=colors.HexColor('#2c3e50'),
                        spaceAfter=12,
                        spaceBefore=12
                    )
                    normal_style = styles['Normal']
                    normal_style.fontSize = 12
                    normal_style.leading = 16

                    # Story (Inhalt)
                    story = []

                    # Titel
                    if add_metadata:
                        story.append(Paragraph("Barrierefreies PDF", title_style))
                        story.append(Paragraph(f"Konvertiert von: {uploaded_file.name}", normal_style))
                        story.append(Spacer(1, 0.3*inch))
                        story.append(PageBreak())

                    # Inhaltsverzeichnis
                    if add_toc:
                        story.append(Paragraph("Inhaltsverzeichnis", heading_style))
                        for i, slide in enumerate(prs.slides, 1):
                            title = f"Folie {i}"
                            for shape in slide.shapes:
                                if hasattr(shape, "text") and shape.text.strip():
                                    title = shape.text.strip()[:50]
                                    break
                            story.append(Paragraph(f"{i}. {title}", normal_style))
                        story.append(PageBreak())

                    # Folien durchgehen
                    for slide_num, slide in enumerate(prs.slides, 1):
                        # Foliennummer
                        story.append(Paragraph(f"Folie {slide_num}", heading_style))
                        story.append(Spacer(1, 0.2*inch))

                        # Text aus Shapes extrahieren
                        for shape in slide.shapes:
                            if hasattr(shape, "text") and shape.text.strip():
                                text = shape.text.strip()
                                # Entscheiden ob Überschrift oder normaler Text
                                if slide_num == 1 or len(text) < 100:
                                    story.append(Paragraph(text, heading_style))
                                else:
                                    story.append(Paragraph(text, normal_style))
                                story.append(Spacer(1, 0.1*inch))

                            # Bilder extrahieren (wenn gewünscht)
                            if include_images and shape.shape_type == 13:  # Picture
                                try:
                                    image = shape.image
                                    image_bytes = image.blob
                                    img = Image.open(io.BytesIO(image_bytes))

                                    # Temporäre Datei für Bild
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                                        img.save(tmp.name, 'PNG')
                                        tmp_path = tmp.name

                                    # Alt-Text wenn vorhanden
                                    alt_text = getattr(shape, 'alt_text', 'Bild aus Präsentation')
                                    if alt_text:
                                        story.append(Paragraph(f"Bildbeschreibung: {alt_text}", normal_style))

                                    # Bild hinzufügen
                                    img_width = min(6*inch, pdf_size[0] - 2*inch)
                                    img_obj = RLImage(tmp_path, width=img_width, height=img_width*img.height/img.width)
                                    story.append(img_obj)
                                    story.append(Spacer(1, 0.2*inch))

                                    # Temp Datei löschen
                                    os.unlink(tmp_path)
                                except Exception as e:
                                    st.warning(f"Konnte Bild auf Folie {slide_num} nicht verarbeiten")

                        # Seitenumbruch nach jeder Folie
                        story.append(PageBreak())

                    # PDF erstellen
                    doc.build(story)
                    pdf_buffer.seek(0)

                    # Download
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### ✅ Konvertierung erfolgreich!")
                    st.markdown("""
                    Das barrierefreie PDF wurde erstellt. Es enthält:
                    - Strukturierte Textebenen
                    - Logische Lesereihenfolge
                    - Metadaten für Barrierefreiheit
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.download_button(
                        label="📥 Barrierefreies PDF herunterladen",
                        data=pdf_buffer,
                        file_name=f"barrierefrei_{uploaded_file.name.replace('.pptx', '.pdf')}",
                        mime="application/pdf",
                        type="primary"
                    )

                except Exception as e:
                    st.error(f"Fehler bei der Konvertierung: {str(e)}")
                    st.info("Bitte stellen Sie sicher, dass die hochgeladene Datei eine gültige PowerPoint-Datei (.pptx) ist.")

# Farbkontrast-Checker
elif tool_option == "Farbkontrast-Checker":
    st.markdown('<h2 class="tool-header">🎨 Farbkontrast-Checker</h2>', unsafe_allow_html=True)

    st.markdown("""
    Überprüfen Sie das Kontrastverhältnis zwischen Vordergrund- und Hintergrundfarben
    gemäß den WCAG 2.1 Richtlinien.

    **WCAG Anforderungen:**
    - **Level AA:** Mindestens 4.5:1 für normalen Text, 3:1 für großen Text
    - **Level AAA:** Mindestens 7:1 für normalen Text, 4.5:1 für großen Text
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Vordergrundfarbe (Text)")
        fg_color = st.color_picker("Wählen Sie die Textfarbe", "#000000")
        st.markdown(f'<div style="background-color: white; color: {fg_color}; padding: 20px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px;">Beispieltext in dieser Farbe</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### Hintergrundfarbe")
        bg_color = st.color_picker("Wählen Sie die Hintergrundfarbe", "#FFFFFF")
        st.markdown(f'<div style="background-color: {bg_color}; padding: 20px; border: 1px solid #ddd; border-radius: 5px; height: 60px;"></div>', unsafe_allow_html=True)

    # Kontrast berechnen
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def relative_luminance(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast_ratio(fg, bg):
        l1 = relative_luminance(hex_to_rgb(fg))
        l2 = relative_luminance(hex_to_rgb(bg))
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    ratio = contrast_ratio(fg_color, bg_color)

    # Vorschau
    st.markdown("### Vorschau")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<div style="background-color: {bg_color}; color: {fg_color}; padding: 30px; border-radius: 5px; font-size: 16px;"><strong>Normaler Text</strong><br>Dies ist ein Beispieltext in normaler Größe (16px)</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div style="background-color: {bg_color}; color: {fg_color}; padding: 30px; border-radius: 5px; font-size: 24px;"><strong>Großer Text</strong><br>Dies ist großer Text (24px)</div>', unsafe_allow_html=True)

    # Ergebnisse
    st.markdown("### Ergebnisse")
    st.markdown(f"**Kontrastverhältnis:** {ratio:.2f}:1")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Level AA")
        normal_aa = ratio >= 4.5
        large_aa = ratio >= 3.0
        st.markdown(f"{'✅' if normal_aa else '❌'} Normaler Text: {'Bestanden' if normal_aa else 'Nicht bestanden'}")
        st.markdown(f"{'✅' if large_aa else '❌'} Großer Text: {'Bestanden' if large_aa else 'Nicht bestanden'}")

    with col2:
        st.markdown("#### Level AAA")
        normal_aaa = ratio >= 7.0
        large_aaa = ratio >= 4.5
        st.markdown(f"{'✅' if normal_aaa else '❌'} Normaler Text: {'Bestanden' if normal_aaa else 'Nicht bestanden'}")
        st.markdown(f"{'✅' if large_aaa else '❌'} Großer Text: {'Bestanden' if large_aaa else 'Nicht bestanden'}")

    # Empfehlungen
    if ratio < 4.5:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        **⚠️ Empfehlung:** Das Kontrastverhältnis ist zu niedrig für barrierefreien Text.
        Erwägen Sie eine dunklere Textfarbe oder einen helleren Hintergrund.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    elif ratio >= 7.0:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("**✅ Ausgezeichnet!** Diese Farbkombination erfüllt die höchsten WCAG-Standards (AAA).")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**✅ Gut!** Diese Farbkombination erfüllt die WCAG Level AA Standards.")
        st.markdown('</div>', unsafe_allow_html=True)

# Alt-Text Generator
elif tool_option == "Alt-Text Generator":
    st.markdown('<h2 class="tool-header">🖼️ Alt-Text Generator</h2>', unsafe_allow_html=True)

    st.markdown("""
    Erstellen Sie aussagekräftige Alternativtexte für Bilder, um diese für Screenreader
    und Menschen mit Sehbehinderungen zugänglich zu machen.

    **Best Practices für Alt-Texte:**
    - Beschreiben Sie den Inhalt und die Funktion des Bildes
    - Halten Sie es prägnant (150 Zeichen oder weniger)
    - Vermeiden Sie "Bild von..." oder "Foto von..."
    - Beschreiben Sie wichtige visuelle Details
    """)

    uploaded_image = st.file_uploader("Laden Sie ein Bild hoch", type=['png', 'jpg', 'jpeg', 'gif', 'webp'])

    if uploaded_image is not None:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### Ihr Bild")
            image = Image.open(uploaded_image)
            st.image(image, use_container_width=True)

            # Bildinfo
            st.markdown("**Bilddetails:**")
            st.write(f"- Format: {image.format}")
            st.write(f"- Größe: {image.size[0]} x {image.size[1]} Pixel")
            st.write(f"- Modus: {image.mode}")

        with col2:
            st.markdown("### Alt-Text erstellen")

            # Kontext
            context = st.text_input("Kontext (optional)", placeholder="z.B. 'Produkt-Seite', 'Blog-Artikel über...'")

            st.markdown("**Manuelle Alt-Text Erstellung:**")
            alt_text = st.text_area(
                "Schreiben Sie eine Beschreibung des Bildes",
                height=150,
                placeholder="Beschreiben Sie, was auf dem Bild zu sehen ist..."
            )

            # Zeichenzähler
            char_count = len(alt_text)
            if char_count > 0:
                color = "green" if char_count <= 125 else "orange" if char_count <= 150 else "red"
                st.markdown(f"<p style='color: {color};'>Zeichen: {char_count} / 125 empfohlen (max. 150)</p>", unsafe_allow_html=True)

            # Vorschläge für verschiedene Bildtypen
            st.markdown("### 💡 Hilfestellung")
            image_type = st.selectbox(
                "Bildtyp",
                ["Auswählen...", "Informatives Bild", "Dekoratives Bild", "Funktionales Bild", "Komplexes Bild/Diagramm"]
            )

            if image_type == "Informatives Bild":
                st.info("Beschreiben Sie die wichtigsten visuellen Informationen, die das Bild vermittelt.")
            elif image_type == "Dekoratives Bild":
                st.info("Verwenden Sie einen leeren Alt-Text (alt=\"\"), da das Bild keine wichtigen Informationen vermittelt.")
                if st.button("Leeren Alt-Text übernehmen"):
                    alt_text = ""
            elif image_type == "Funktionales Bild":
                st.info("Beschreiben Sie die Funktion oder Aktion, nicht das Aussehen (z.B. 'Suchen' statt 'Lupe').")
            elif image_type == "Komplexes Bild/Diagramm":
                st.info("Geben Sie eine kurze Zusammenfassung im Alt-Text und erwägen Sie eine ausführliche Beschreibung im umgebenden Text.")

            if alt_text:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown("**Ihr Alt-Text:**")
                st.code(f'<img src="bild.jpg" alt="{alt_text}">', language="html")
                st.markdown('</div>', unsafe_allow_html=True)

                # Bewertung
                st.markdown("### Bewertung")
                checks = []
                checks.append(("Länge angemessen", len(alt_text) <= 150))
                checks.append(("Beginnt nicht mit 'Bild von'", not alt_text.lower().startswith(('bild', 'foto', 'grafik'))))
                checks.append(("Enthält Beschreibung", len(alt_text.split()) >= 3))

                for check_name, passed in checks:
                    st.markdown(f"{'✅' if passed else '❌'} {check_name}")

# PDF Prüfer
elif tool_option == "PDF Prüfer":
    st.markdown('<h2 class="tool-header">📄 PDF Barrierefreiheitsprüfer</h2>', unsafe_allow_html=True)

    st.markdown("""
    Analysieren Sie PDF-Dokumente auf Barrierefreiheit und erhalten Sie Empfehlungen
    zur Verbesserung.

    **Geprüfte Aspekte:**
    - Textextraktion (Screenreader-Kompatibilität)
    - Dokumentstruktur und Metadaten
    - Bilder und Alternativtexte
    - Seitenorganisation
    """)

    uploaded_pdf = st.file_uploader("Laden Sie ein PDF-Dokument hoch", type=['pdf'])

    if uploaded_pdf is not None:
        st.success(f"PDF '{uploaded_pdf.name}' erfolgreich hochgeladen!")

        if st.button("PDF auf Barrierefreiheit prüfen", type="primary"):
            with st.spinner("Analysiere PDF..."):
                try:
                    # PDF mit PyMuPDF öffnen
                    pdf_data = uploaded_pdf.read()
                    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

                    # Basis-Informationen
                    st.markdown("### 📊 Dokument-Informationen")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Anzahl Seiten", pdf_document.page_count)
                        st.metric("Dateiformat", "PDF")

                    with col2:
                        metadata = pdf_document.metadata
                        has_metadata = bool(metadata and any(metadata.values()))
                        st.metric("Metadaten vorhanden", "✅ Ja" if has_metadata else "❌ Nein")

                    # Metadaten Details
                    if has_metadata:
                        with st.expander("Metadaten anzeigen"):
                            for key, value in metadata.items():
                                if value:
                                    st.write(f"**{key}:** {value}")

                    # Text-Extraktion
                    st.markdown("### 📝 Text-Analyse")
                    total_text = ""
                    text_pages = 0

                    for page_num in range(pdf_document.page_count):
                        page = pdf_document[page_num]
                        text = page.get_text()
                        if text.strip():
                            text_pages += 1
                            total_text += text

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Seiten mit Text", f"{text_pages} / {pdf_document.page_count}")
                    with col2:
                        word_count = len(total_text.split())
                        st.metric("Wörter gesamt", f"{word_count:,}")

                    # Textvorschau
                    if total_text:
                        with st.expander("Textvorschau (erste 500 Zeichen)"):
                            st.text(total_text[:500] + "...")

                    # Bilder-Analyse
                    st.markdown("### 🖼️ Bilder-Analyse")
                    total_images = 0

                    for page_num in range(pdf_document.page_count):
                        page = pdf_document[page_num]
                        images = page.get_images()
                        total_images += len(images)

                    st.metric("Gefundene Bilder", total_images)

                    if total_images > 0:
                        st.warning("⚠️ Bilder gefunden. Bitte stellen Sie sicher, dass alle Bilder Alternativtexte haben.")

                    # Barrierefreiheits-Bewertung
                    st.markdown("### ✅ Barrierefreiheits-Bewertung")

                    checks = []
                    checks.append(("Text extrahierbar (Screenreader-kompatibel)", text_pages > 0))
                    checks.append(("Metadaten vorhanden", has_metadata))
                    checks.append(("Dokumenttitel gesetzt", bool(metadata.get('title'))))
                    checks.append(("Dokumentsprache festgelegt", bool(metadata.get('subject'))))
                    checks.append(("Ausreichend Textinhalt", word_count > 50))

                    passed_checks = sum(1 for _, passed in checks if passed)
                    total_checks = len(checks)

                    progress = passed_checks / total_checks
                    st.progress(progress)
                    st.write(f"**Score: {passed_checks}/{total_checks}** ({int(progress*100)}%)")

                    for check_name, passed in checks:
                        st.markdown(f"{'✅' if passed else '❌'} {check_name}")

                    # Empfehlungen
                    st.markdown("### 💡 Empfehlungen")

                    recommendations = []

                    if not has_metadata:
                        recommendations.append("Fügen Sie Metadaten (Titel, Autor, Beschreibung) hinzu")
                    if not metadata.get('title'):
                        recommendations.append("Setzen Sie einen aussagekräftigen Dokumenttitel")
                    if total_images > 0:
                        recommendations.append("Überprüfen Sie, ob alle Bilder Alternativtexte haben")
                    if text_pages < pdf_document.page_count:
                        recommendations.append("Einige Seiten enthalten keinen extrahierbaren Text - möglicherweise gescannte Bilder")
                    if word_count < 50:
                        recommendations.append("Das Dokument enthält sehr wenig Text")

                    recommendations.append("Verwenden Sie strukturierte Überschriften (H1, H2, etc.)")
                    recommendations.append("Stellen Sie sicher, dass das PDF getaggt ist")
                    recommendations.append("Überprüfen Sie die Lesereihenfolge")
                    recommendations.append("Verwenden Sie ausreichende Farbkontraste")

                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")

                    pdf_document.close()

                except Exception as e:
                    st.error(f"Fehler bei der PDF-Analyse: {str(e)}")

# Text-zu-Sprache
elif tool_option == "Text-zu-Sprache":
    st.markdown('<h2 class="tool-header">🔊 Text-zu-Sprache Konverter</h2>', unsafe_allow_html=True)

    st.markdown("""
    Konvertieren Sie Text in Audiodateien, um Inhalte für Menschen mit Sehbehinderungen
    oder Leseproblemen zugänglich zu machen.

    **Anwendungsfälle:**
    - Hörbuch-Versionen von Dokumenten
    - Audiodeskriptionen
    - Barrierefreie Web-Inhalte
    - Lernmaterialien
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        text_input = st.text_area(
            "Geben Sie den Text ein, der in Sprache umgewandelt werden soll",
            height=300,
            placeholder="Geben Sie hier Ihren Text ein oder fügen Sie ihn ein..."
        )

    with col2:
        st.markdown("### Einstellungen")
        language = st.selectbox(
            "Sprache",
            [
                ("Deutsch", "de"),
                ("Englisch", "en"),
                ("Französisch", "fr"),
                ("Spanisch", "es"),
                ("Italienisch", "it"),
                ("Niederländisch", "nl"),
                ("Polnisch", "pl"),
                ("Portugiesisch", "pt"),
                ("Russisch", "ru"),
                ("Türkisch", "tr")
            ],
            format_func=lambda x: x[0]
        )

        slow_speed = st.checkbox("Langsame Geschwindigkeit", value=False)

        st.markdown("### Statistik")
        char_count = len(text_input)
        word_count = len(text_input.split())
        st.write(f"Zeichen: {char_count:,}")
        st.write(f"Wörter: {word_count:,}")
        est_duration = word_count * 0.4  # Grobe Schätzung: 150 Wörter/Minute
        st.write(f"Geschätzte Dauer: ~{int(est_duration)}s")

    if text_input:
        if st.button("🎵 Audio generieren", type="primary"):
            with st.spinner("Generiere Audio..."):
                try:
                    # Text-zu-Sprache mit gTTS
                    tts = gTTS(text=text_input, lang=language[1], slow=slow_speed)

                    # Temporäre Datei
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                        tts.save(tmp_file.name)
                        tmp_file.seek(0)

                        # Audio abspielen
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.markdown("### ✅ Audio erfolgreich generiert!")
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Audio player
                        audio_file = open(tmp_file.name, 'rb')
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format='audio/mp3')

                        # Download
                        st.download_button(
                            label="📥 Audio-Datei herunterladen",
                            data=audio_bytes,
                            file_name="text_zu_sprache.mp3",
                            mime="audio/mp3",
                            type="primary"
                        )

                        audio_file.close()
                        os.unlink(tmp_file.name)

                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("""
                    **💡 Verwendungshinweise:**
                    - Die Audiodatei kann auf Webseiten eingebettet werden
                    - Stellen Sie Steuerelemente (Play/Pause) bereit
                    - Bieten Sie auch eine Textversion an
                    - Verwenden Sie beschreibende Dateinamen
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Fehler bei der Audio-Generierung: {str(e)}")
    else:
        st.info("👆 Geben Sie Text ein, um zu beginnen")

# Word zu PDF Konverter
elif tool_option == "Word zu PDF":
    st.markdown('<h2 class="tool-header">📝 Word zu barrierefreiem PDF</h2>', unsafe_allow_html=True)

    st.markdown("""
    Konvertieren Sie Word-Dokumente (.docx) in barrierefreie PDF-Dokumente.
    Das Tool extrahiert Text, Überschriften und Formatierungen und erstellt
    ein strukturiertes, barrierefreies PDF.
    """)

    uploaded_docx = st.file_uploader("Laden Sie eine Word-Datei hoch", type=['docx'])

    if uploaded_docx is not None:
        st.success(f"Datei '{uploaded_docx.name}' erfolgreich hochgeladen!")

        col1, col2 = st.columns(2)
        with col1:
            include_headers = st.checkbox("Überschriften als Tags", value=True)
            add_toc = st.checkbox("Inhaltsverzeichnis erstellen", value=True)
        with col2:
            page_size = st.selectbox("Seitengröße", ["A4", "Letter"], key="docx_page_size")
            preserve_formatting = st.checkbox("Formatierung beibehalten", value=True)

        if st.button("In barrierefreies PDF konvertieren", type="primary", key="docx_convert"):
            with st.spinner("Konvertierung läuft..."):
                try:
                    doc = Document(uploaded_docx)
                    pdf_buffer = io.BytesIO()
                    pdf_size = A4 if page_size == "A4" else letter
                    pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=pdf_size)

                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle(
                        'DocTitle', parent=styles['Heading1'],
                        fontSize=24, textColor=colors.HexColor('#1f77b4'),
                        spaceAfter=30, alignment=TA_CENTER
                    )
                    h1_style = ParagraphStyle(
                        'H1', parent=styles['Heading1'],
                        fontSize=18, textColor=colors.HexColor('#2c3e50'),
                        spaceAfter=12, spaceBefore=20
                    )
                    h2_style = ParagraphStyle(
                        'H2', parent=styles['Heading2'],
                        fontSize=14, textColor=colors.HexColor('#34495e'),
                        spaceAfter=8, spaceBefore=12
                    )
                    normal_style = styles['Normal']
                    normal_style.fontSize = 11
                    normal_style.leading = 14

                    story = []
                    story.append(Paragraph("Barrierefreies PDF", title_style))
                    story.append(Paragraph(f"Konvertiert aus: {uploaded_docx.name}", normal_style))
                    story.append(Spacer(1, 0.5*inch))

                    # Inhaltsverzeichnis erstellen
                    if add_toc:
                        toc_entries = []
                        for para in doc.paragraphs:
                            if para.style.name.startswith('Heading'):
                                toc_entries.append(para.text[:60])
                        if toc_entries:
                            story.append(Paragraph("Inhaltsverzeichnis", h1_style))
                            for i, entry in enumerate(toc_entries, 1):
                                story.append(Paragraph(f"{i}. {entry}", normal_style))
                            story.append(PageBreak())

                    # Dokument-Inhalt
                    for para in doc.paragraphs:
                        text = para.text.strip()
                        if not text:
                            story.append(Spacer(1, 0.1*inch))
                            continue

                        if para.style.name.startswith('Heading 1') or para.style.name == 'Title':
                            story.append(Paragraph(text, h1_style))
                        elif para.style.name.startswith('Heading'):
                            story.append(Paragraph(text, h2_style))
                        else:
                            story.append(Paragraph(text, normal_style))

                    # Tabellen extrahieren
                    for table in doc.tables:
                        table_data = []
                        for row in table.rows:
                            row_data = [cell.text for cell in row.cells]
                            table_data.append(row_data)
                        if table_data:
                            t = Table(table_data)
                            t.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]))
                            story.append(Spacer(1, 0.2*inch))
                            story.append(t)
                            story.append(Spacer(1, 0.2*inch))

                    pdf_doc.build(story)
                    pdf_buffer.seek(0)

                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### ✅ Konvertierung erfolgreich!")
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.download_button(
                        label="📥 Barrierefreies PDF herunterladen",
                        data=pdf_buffer,
                        file_name=f"barrierefrei_{uploaded_docx.name.replace('.docx', '.pdf')}",
                        mime="application/pdf",
                        type="primary"
                    )

                except Exception as e:
                    st.error(f"Fehler bei der Konvertierung: {str(e)}")

# HTML Barrierefreiheits-Checker
elif tool_option == "HTML Checker":
    st.markdown('<h2 class="tool-header">🌐 HTML Barrierefreiheits-Checker</h2>', unsafe_allow_html=True)

    st.markdown("""
    Überprüfen Sie HTML-Code auf häufige Barrierefreiheitsprobleme gemäß WCAG 2.1.
    Der Checker analysiert Ihren Code und gibt konkrete Verbesserungsvorschläge.
    """)

    html_input = st.text_area(
        "Fügen Sie Ihren HTML-Code ein",
        height=300,
        placeholder='<html>\n  <body>\n    <img src="bild.jpg">\n    <div onclick="click()">\n  </body>\n</html>'
    )

    if html_input and st.button("HTML prüfen", type="primary"):
        issues = []
        warnings = []
        passed = []

        # Prüfungen durchführen
        # 1. Alt-Text für Bilder
        img_tags = re.findall(r'<img[^>]*>', html_input, re.IGNORECASE)
        img_without_alt = [tag for tag in img_tags if 'alt=' not in tag.lower()]
        if img_without_alt:
            issues.append(f"🔴 {len(img_without_alt)} Bild(er) ohne alt-Attribut gefunden")
        elif img_tags:
            passed.append("✅ Alle Bilder haben alt-Attribute")

        # 2. Leere alt-Attribute prüfen
        empty_alts = re.findall(r'alt=["\']\s*["\']', html_input)
        if empty_alts:
            warnings.append(f"🟡 {len(empty_alts)} leere alt-Attribute gefunden (nur für dekorative Bilder erlaubt)")

        # 3. Sprache definiert
        if 'lang=' not in html_input.lower():
            issues.append("🔴 Keine Sprachdeklaration (lang-Attribut) im HTML gefunden")
        else:
            passed.append("✅ Sprache ist deklariert")

        # 4. Überschriften-Hierarchie
        h_tags = re.findall(r'<h([1-6])[^>]*>', html_input, re.IGNORECASE)
        if h_tags:
            h_levels = [int(h) for h in h_tags]
            if h_levels[0] != 1:
                issues.append("🔴 Die erste Überschrift sollte <h1> sein")
            else:
                passed.append("✅ Überschriften-Hierarchie beginnt mit H1")
        else:
            warnings.append("🟡 Keine Überschriften gefunden")

        # 5. Formulare mit Labels
        inputs = re.findall(r'<input[^>]*>', html_input, re.IGNORECASE)
        labels = re.findall(r'<label[^>]*>', html_input, re.IGNORECASE)
        if inputs and len(labels) < len(inputs):
            issues.append(f"🔴 Möglicherweise fehlende Labels für Formularelemente ({len(inputs)} inputs, {len(labels)} labels)")

        # 6. ARIA-Attribute
        aria_attrs = re.findall(r'aria-[a-z]+', html_input, re.IGNORECASE)
        role_attrs = re.findall(r'role=', html_input, re.IGNORECASE)
        if aria_attrs or role_attrs:
            passed.append(f"✅ ARIA-Attribute werden verwendet ({len(aria_attrs)} aria-*, {len(role_attrs)} role)")

        # 7. Tabellen mit Headern
        tables = re.findall(r'<table[^>]*>.*?</table>', html_input, re.IGNORECASE | re.DOTALL)
        for table in tables:
            if '<th' not in table.lower():
                warnings.append("🟡 Tabelle ohne Kopfzellen (<th>) gefunden")

        # 8. Link-Text prüfen
        link_texts = re.findall(r'<a[^>]*>([^<]*)</a>', html_input, re.IGNORECASE)
        bad_links = [t for t in link_texts if t.lower().strip() in ['hier', 'klick', 'hier klicken', 'mehr', 'click here', 'read more']]
        if bad_links:
            warnings.append(f"🟡 {len(bad_links)} unspezifische Link-Texte gefunden ('hier klicken' etc.)")
        elif link_texts:
            passed.append("✅ Link-Texte sind aussagekräftig")

        # 9. onclick ohne keyboard alternative
        onclick_divs = re.findall(r'<(?:div|span)[^>]*onclick[^>]*>', html_input, re.IGNORECASE)
        for div in onclick_divs:
            if 'tabindex' not in div.lower() and 'role="button"' not in div.lower():
                issues.append("🔴 Interaktives Element ohne Tastaturunterstützung gefunden")
                break

        # 10. Title-Tag
        if '<title>' not in html_input.lower() or '<title></title>' in html_input.lower():
            warnings.append("🟡 Kein oder leerer <title>-Tag gefunden")
        else:
            passed.append("✅ Seitentitel vorhanden")

        # Ergebnisse anzeigen
        st.markdown("### 📊 Prüfergebnis")

        total_checks = len(issues) + len(warnings) + len(passed)
        score = (len(passed) / total_checks * 100) if total_checks > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fehler", len(issues), delta=None)
        with col2:
            st.metric("Warnungen", len(warnings), delta=None)
        with col3:
            st.metric("Bestanden", len(passed), delta=None)

        st.progress(score / 100)
        st.write(f"**Score: {score:.0f}%**")

        if issues:
            st.markdown("### ❌ Fehler (müssen behoben werden)")
            for issue in issues:
                st.markdown(issue)

        if warnings:
            st.markdown("### ⚠️ Warnungen (sollten geprüft werden)")
            for warning in warnings:
                st.markdown(warning)

        if passed:
            st.markdown("### ✅ Bestanden")
            for p in passed:
                st.markdown(p)

        # Empfehlungen
        st.markdown("### 💡 Empfehlungen")
        st.markdown("""
        - Fügen Sie allen informativen Bildern aussagekräftige alt-Texte hinzu
        - Verwenden Sie semantische HTML-Elemente (<nav>, <main>, <article>, etc.)
        - Stellen Sie sicher, dass alle Formularfelder Labels haben
        - Testen Sie die Tastaturnavigation
        - Prüfen Sie Farbkontraste mit dem Kontrast-Checker
        """)

# Leichte Sprache Vereinfacher
elif tool_option == "Leichte Sprache":
    st.markdown('<h2 class="tool-header">📖 Leichte Sprache Analyse</h2>', unsafe_allow_html=True)

    st.markdown("""
    Analysieren Sie Texte auf ihre Verständlichkeit und erhalten Sie Hinweise
    zur Vereinfachung für Leichte Sprache gemäß den Regeln für Leichte Sprache.

    **Merkmale Leichter Sprache:**
    - Kurze Sätze (max. 8-12 Wörter)
    - Einfache Wörter
    - Aktive Sprache
    - Keine Fremdwörter
    - Ein Satz pro Zeile
    """)

    text_input = st.text_area(
        "Geben Sie den zu analysierenden Text ein",
        height=250,
        placeholder="Fügen Sie hier Ihren Text ein..."
    )

    if text_input:
        # Analyse durchführen
        sentences = re.split(r'[.!?]+', text_input)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = text_input.split()
        total_words = len(words)
        total_sentences = len(sentences)

        # Durchschnittliche Satzlänge
        avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0

        # Lange Wörter (mehr als 10 Zeichen)
        long_words = [w for w in words if len(re.sub(r'[^\w]', '', w)) > 10]

        # Fremdwörter-Indikatoren (vereinfacht)
        foreign_indicators = ['tion', 'ismus', 'ität', 'ieren', 'ierung', 'iv', 'ell']
        potential_foreign = [w for w in words if any(ind in w.lower() for ind in foreign_indicators)]

        # Passiv-Indikatoren
        passive_indicators = ['wird', 'werden', 'wurde', 'wurden', 'worden']
        passive_count = sum(1 for w in words if w.lower() in passive_indicators)

        # Lesbarkeitsindex (vereinfachte Flesch-Reading-Ease Adaptation für Deutsch)
        syllables_per_word = sum(len(re.findall(r'[aeiouäöü]+', w.lower())) for w in words) / max(total_words, 1)
        readability = 180 - avg_sentence_length - (58.5 * syllables_per_word)
        readability = max(0, min(100, readability))

        st.markdown("### 📊 Analyse-Ergebnis")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Wörter gesamt", total_words)
            st.metric("Sätze gesamt", total_sentences)
        with col2:
            color = "green" if avg_sentence_length <= 10 else "orange" if avg_sentence_length <= 15 else "red"
            st.metric("Ø Satzlänge", f"{avg_sentence_length:.1f} Wörter")
            st.metric("Lange Wörter", len(long_words))
        with col3:
            st.metric("Lesbarkeitsindex", f"{readability:.0f}/100")
            st.metric("Passiv-Konstrukte", passive_count)

        # Bewertung
        st.markdown("### ✅ Bewertung für Leichte Sprache")

        checks = []
        if avg_sentence_length <= 10:
            checks.append(("✅", "Satzlänge optimal (≤10 Wörter)"))
        elif avg_sentence_length <= 15:
            checks.append(("🟡", f"Satzlänge akzeptabel, aber verkürzbar ({avg_sentence_length:.1f} Wörter)"))
        else:
            checks.append(("❌", f"Sätze zu lang ({avg_sentence_length:.1f} Wörter, max. 10 empfohlen)"))

        if len(long_words) == 0:
            checks.append(("✅", "Keine überlangen Wörter"))
        else:
            checks.append(("🟡", f"{len(long_words)} lange Wörter gefunden"))

        if passive_count == 0:
            checks.append(("✅", "Kein Passiv erkannt"))
        else:
            checks.append(("🟡", f"{passive_count} mögliche Passiv-Konstrukte"))

        if len(potential_foreign) == 0:
            checks.append(("✅", "Keine offensichtlichen Fremdwörter"))
        else:
            checks.append(("🟡", f"{len(potential_foreign)} mögliche Fremdwörter"))

        for icon, text in checks:
            st.markdown(f"{icon} {text}")

        # Detailanalyse
        with st.expander("📝 Detailierte Satzanalyse"):
            for i, sentence in enumerate(sentences, 1):
                word_count = len(sentence.split())
                if word_count > 15:
                    st.markdown(f"**Satz {i}** ({word_count} Wörter) ❌: {sentence}")
                elif word_count > 10:
                    st.markdown(f"**Satz {i}** ({word_count} Wörter) 🟡: {sentence}")
                else:
                    st.markdown(f"**Satz {i}** ({word_count} Wörter) ✅: {sentence}")

        if long_words:
            with st.expander("📚 Lange Wörter"):
                for word in set(long_words):
                    st.write(f"- {word}")

        if potential_foreign:
            with st.expander("🌍 Mögliche Fremdwörter"):
                for word in set(potential_foreign):
                    st.write(f"- {word}")

        # Tipps
        st.markdown("### 💡 Tipps für Leichte Sprache")
        st.markdown("""
        1. **Kurze Sätze:** Teilen Sie lange Sätze in mehrere kurze Sätze auf
        2. **Einfache Wörter:** Ersetzen Sie Fremdwörter durch deutsche Wörter
        3. **Aktiv statt Passiv:** "Wir prüfen" statt "Es wird geprüft"
        4. **Bindestriche:** Teilen Sie lange Wörter: Bundes-Regierung
        5. **Erklärungen:** Erklären Sie schwierige Begriffe
        6. **Bilder:** Nutzen Sie Bilder zur Unterstützung
        """)

# ARIA Helper
elif tool_option == "ARIA Helper":
    st.markdown('<h2 class="tool-header">♿ ARIA-Attribut Helper</h2>', unsafe_allow_html=True)

    st.markdown("""
    ARIA (Accessible Rich Internet Applications) macht dynamische Webinhalte
    für Screenreader zugänglich. Dieses Tool hilft Ihnen bei der korrekten
    Verwendung von ARIA-Attributen.
    """)

    tab1, tab2, tab3 = st.tabs(["🎭 Rollen", "📝 Attribute", "🔧 Generator"])

    with tab1:
        st.markdown("### ARIA-Rollen Übersicht")

        role_category = st.selectbox(
            "Kategorie auswählen",
            ["Landmark-Rollen", "Widget-Rollen", "Dokumentstruktur-Rollen", "Live-Region-Rollen"]
        )

        roles_data = {
            "Landmark-Rollen": {
                "banner": "Kopfbereich der Seite, meist mit Logo und Navigation",
                "navigation": "Navigationsbereich mit Links",
                "main": "Hauptinhalt der Seite",
                "complementary": "Ergänzender Inhalt (Sidebar)",
                "contentinfo": "Footer mit Copyright, Impressum etc.",
                "search": "Suchfunktion",
                "form": "Formularbereich",
                "region": "Benannter Seitenbereich"
            },
            "Widget-Rollen": {
                "button": "Klickbares Schaltflächen-Element",
                "checkbox": "Auswahl-Box (an/aus)",
                "dialog": "Modales Dialogfenster",
                "menuitem": "Element in einem Menü",
                "progressbar": "Fortschrittsanzeige",
                "slider": "Schieberegler",
                "tab": "Tab in einer Tablist",
                "tabpanel": "Inhalt eines Tabs",
                "textbox": "Texteingabefeld",
                "tooltip": "Hinweistext bei Hover"
            },
            "Dokumentstruktur-Rollen": {
                "article": "Eigenständiger Artikelinhalt",
                "heading": "Überschrift (nutze aria-level)",
                "list": "Liste von Elementen",
                "listitem": "Element einer Liste",
                "table": "Datentabelle",
                "row": "Tabellenzeile",
                "cell": "Tabellenzelle",
                "img": "Bild oder Grafik"
            },
            "Live-Region-Rollen": {
                "alert": "Wichtige Statusmeldung (unterbricht)",
                "log": "Chat oder Aktivitätsprotokoll",
                "status": "Statusmeldung (unterbricht nicht)",
                "timer": "Zeitanzeige oder Countdown"
            }
        }

        for role, description in roles_data[role_category].items():
            st.markdown(f"**`role=\"{role}\"`** - {description}")
            st.code(f'<div role="{role}">Inhalt</div>', language="html")

    with tab2:
        st.markdown("### Wichtige ARIA-Attribute")

        attr_data = {
            "aria-label": {
                "beschreibung": "Unsichtbares Label für Element",
                "beispiel": '<button aria-label="Menü öffnen"><svg>...</svg></button>'
            },
            "aria-labelledby": {
                "beschreibung": "Referenziert sichtbares Label per ID",
                "beispiel": '<h2 id="section1">Kontakt</h2>\n<section aria-labelledby="section1">...</section>'
            },
            "aria-describedby": {
                "beschreibung": "Referenziert beschreibenden Text",
                "beispiel": '<input aria-describedby="help">\n<span id="help">Mind. 8 Zeichen</span>'
            },
            "aria-hidden": {
                "beschreibung": "Versteckt Element vor Screenreadern",
                "beispiel": '<span aria-hidden="true">🎨</span> Farbauswahl'
            },
            "aria-expanded": {
                "beschreibung": "Zeigt an, ob Element aufgeklappt ist",
                "beispiel": '<button aria-expanded="false">Details anzeigen</button>'
            },
            "aria-live": {
                "beschreibung": "Kennzeichnet dynamisch aktualisierte Bereiche",
                "beispiel": '<div aria-live="polite">3 neue Nachrichten</div>'
            },
            "aria-current": {
                "beschreibung": "Kennzeichnet aktuelle Position",
                "beispiel": '<a aria-current="page" href="/">Startseite</a>'
            },
            "aria-required": {
                "beschreibung": "Kennzeichnet Pflichtfeld",
                "beispiel": '<input aria-required="true" type="text">'
            }
        }

        for attr, data in attr_data.items():
            with st.expander(f"**{attr}**"):
                st.markdown(data["beschreibung"])
                st.code(data["beispiel"], language="html")

    with tab3:
        st.markdown("### ARIA-Code Generator")

        element_type = st.selectbox(
            "Element-Typ",
            ["Button", "Link als Button", "Icon-Button", "Dialog", "Tab-Navigation", "Accordion", "Alert", "Suche"]
        )

        generated_code = ""

        if element_type == "Button":
            label = st.text_input("Button-Text", "Absenden")
            disabled = st.checkbox("Deaktiviert")
            generated_code = f'<button type="button"{" disabled" if disabled else ""}{" aria-disabled=\"true\"" if disabled else ""}>{label}</button>'

        elif element_type == "Link als Button":
            label = st.text_input("Button-Text", "Aktion ausführen")
            generated_code = f'<a href="#" role="button" tabindex="0">{label}</a>'

        elif element_type == "Icon-Button":
            label = st.text_input("Beschreibung (für Screenreader)", "Menü öffnen")
            icon = st.text_input("Icon (z.B. Emoji oder SVG)", "☰")
            generated_code = f'<button type="button" aria-label="{label}">\n  <span aria-hidden="true">{icon}</span>\n</button>'

        elif element_type == "Dialog":
            title = st.text_input("Dialog-Titel", "Bestätigung")
            generated_code = f'''<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">{title}</h2>
  <div>Dialog-Inhalt hier...</div>
  <button type="button">Schließen</button>
</div>'''

        elif element_type == "Tab-Navigation":
            tabs = st.text_input("Tab-Namen (kommagetrennt)", "Tab 1, Tab 2, Tab 3")
            tab_list = [t.strip() for t in tabs.split(",")]
            tab_html = ""
            panel_html = ""
            for i, tab in enumerate(tab_list):
                selected = "true" if i == 0 else "false"
                tabindex = "0" if i == 0 else "-1"
                hidden = "" if i == 0 else " hidden"
                tab_html += f'  <button role="tab" aria-selected="{selected}" aria-controls="panel-{i}" tabindex="{tabindex}">{tab}</button>\n'
                panel_html += f'<div role="tabpanel" id="panel-{i}"{hidden}>{tab} Inhalt</div>\n'
            generated_code = f'<div role="tablist">\n{tab_html}</div>\n{panel_html}'

        elif element_type == "Accordion":
            title = st.text_input("Überschrift", "Mehr anzeigen")
            generated_code = f'''<h3>
  <button aria-expanded="false" aria-controls="accordion-content">
    {title}
  </button>
</h3>
<div id="accordion-content" hidden>
  Ausgeklappter Inhalt hier...
</div>'''

        elif element_type == "Alert":
            message = st.text_input("Nachricht", "Ihre Änderungen wurden gespeichert.")
            alert_type = st.selectbox("Typ", ["status", "alert"])
            generated_code = f'<div role="{alert_type}" aria-live="{"assertive" if alert_type == "alert" else "polite"}">\n  {message}\n</div>'

        elif element_type == "Suche":
            placeholder = st.text_input("Platzhalter", "Suchen...")
            generated_code = f'''<search role="search">
  <label for="search-input" class="visually-hidden">Suche</label>
  <input type="search" id="search-input" placeholder="{placeholder}">
  <button type="submit" aria-label="Suche starten">
    <span aria-hidden="true">🔍</span>
  </button>
</search>'''

        st.markdown("### Generierter Code")
        st.code(generated_code, language="html")

        st.markdown("### 💡 Best Practices")
        st.markdown("""
        - Verwenden Sie semantisches HTML, bevor Sie ARIA nutzen
        - Fügen Sie keine unnötigen ARIA-Attribute hinzu
        - Testen Sie mit echten Screenreadern (NVDA, VoiceOver)
        - Stellen Sie Tastaturnavigation sicher
        """)

# Untertitel Generator
elif tool_option == "Untertitel Generator":
    st.markdown('<h2 class="tool-header">🎬 Untertitel Generator</h2>', unsafe_allow_html=True)

    st.markdown("""
    Erstellen Sie Untertitel und Transkripte für Videos. Exportieren Sie im
    SRT- oder VTT-Format für maximale Kompatibilität.

    **Unterstützte Formate:**
    - **SRT** - SubRip (YouTube, VLC, etc.)
    - **VTT** - WebVTT (HTML5 Video)
    """)

    tab1, tab2 = st.tabs(["📝 Manuell erstellen", "📄 Text importieren"])

    with tab1:
        st.markdown("### Untertitel manuell erstellen")

        if 'subtitles' not in st.session_state:
            st.session_state.subtitles = []

        col1, col2 = st.columns(2)
        with col1:
            start_time = st.text_input("Startzeit (HH:MM:SS,mmm)", "00:00:00,000", key="start")
        with col2:
            end_time = st.text_input("Endzeit (HH:MM:SS,mmm)", "00:00:05,000", key="end")

        subtitle_text = st.text_area("Untertitel-Text", height=100, key="subtext")

        if st.button("➕ Untertitel hinzufügen"):
            if subtitle_text:
                st.session_state.subtitles.append({
                    "start": start_time,
                    "end": end_time,
                    "text": subtitle_text
                })
                st.success("Untertitel hinzugefügt!")

        if st.session_state.subtitles:
            st.markdown("### Aktuelle Untertitel")
            for i, sub in enumerate(st.session_state.subtitles):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{i+1}.** [{sub['start']} → {sub['end']}]")
                    st.text(sub['text'])
                with col2:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.subtitles.pop(i)
                        st.rerun()

            # Export
            st.markdown("### Export")
            export_format = st.selectbox("Format", ["SRT", "VTT"])

            if export_format == "SRT":
                srt_content = ""
                for i, sub in enumerate(st.session_state.subtitles, 1):
                    srt_content += f"{i}\n{sub['start']} --> {sub['end']}\n{sub['text']}\n\n"
                st.download_button(
                    "📥 SRT herunterladen",
                    srt_content,
                    "untertitel.srt",
                    "text/plain"
                )
            else:
                vtt_content = "WEBVTT\n\n"
                for i, sub in enumerate(st.session_state.subtitles, 1):
                    start_vtt = sub['start'].replace(',', '.')
                    end_vtt = sub['end'].replace(',', '.')
                    vtt_content += f"{i}\n{start_vtt} --> {end_vtt}\n{sub['text']}\n\n"
                st.download_button(
                    "📥 VTT herunterladen",
                    vtt_content,
                    "untertitel.vtt",
                    "text/vtt"
                )

            if st.button("🗑️ Alle löschen"):
                st.session_state.subtitles = []
                st.rerun()

    with tab2:
        st.markdown("### Transkript importieren")
        st.markdown("""
        Importieren Sie ein Texttranskript und verteilen Sie es automatisch
        auf Untertitel mit festgelegter Dauer.
        """)

        transcript = st.text_area(
            "Transkript (ein Untertitel pro Zeile)",
            height=200,
            placeholder="Willkommen zu unserem Video.\nHeute zeigen wir Ihnen...\nLos geht's!"
        )

        col1, col2 = st.columns(2)
        with col1:
            start_offset = st.number_input("Startzeit (Sekunden)", 0, 3600, 0)
        with col2:
            duration = st.number_input("Dauer pro Untertitel (Sekunden)", 1, 30, 4)

        if transcript and st.button("Untertitel generieren", type="primary"):
            lines = [line.strip() for line in transcript.split('\n') if line.strip()]

            generated_srt = ""
            generated_vtt = "WEBVTT\n\n"

            current_time = start_offset

            for i, line in enumerate(lines, 1):
                start_sec = current_time
                end_sec = current_time + duration

                # SRT Zeit formatieren
                start_srt = f"{int(start_sec//3600):02d}:{int((start_sec%3600)//60):02d}:{int(start_sec%60):02d},000"
                end_srt = f"{int(end_sec//3600):02d}:{int((end_sec%3600)//60):02d}:{int(end_sec%60):02d},000"

                # VTT Zeit formatieren
                start_vtt = f"{int(start_sec//3600):02d}:{int((start_sec%3600)//60):02d}:{int(start_sec%60):02d}.000"
                end_vtt = f"{int(end_sec//3600):02d}:{int((end_sec%3600)//60):02d}:{int(end_sec%60):02d}.000"

                generated_srt += f"{i}\n{start_srt} --> {end_srt}\n{line}\n\n"
                generated_vtt += f"{i}\n{start_vtt} --> {end_vtt}\n{line}\n\n"

                current_time = end_sec

            st.markdown("### Vorschau")
            st.text(generated_srt[:500] + "..." if len(generated_srt) > 500 else generated_srt)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 SRT herunterladen",
                    generated_srt,
                    "transkript.srt",
                    "text/plain"
                )
            with col2:
                st.download_button(
                    "📥 VTT herunterladen",
                    generated_vtt,
                    "transkript.vtt",
                    "text/vtt"
                )

    st.markdown("### 💡 Tipps für barrierefreie Untertitel")
    st.markdown("""
    - Beschreiben Sie auch wichtige Geräusche: [Türklingel], [Musik]
    - Kennzeichnen Sie Sprecher bei mehreren Personen
    - Halten Sie Untertitel unter 2 Zeilen
    - Synchronisieren Sie mit dem gesprochenen Wort
    - Verwenden Sie korrekte Rechtschreibung und Zeichensetzung
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Barrierefreiheits-Tools</strong> | Entwickelt mit ❤️ für eine zugänglichere digitale Welt</p>
    <p style='font-size: 0.9rem;'>Basierend auf WCAG 2.1 Richtlinien (Web Content Accessibility Guidelines)</p>
</div>
""", unsafe_allow_html=True)
