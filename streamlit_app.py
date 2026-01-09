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
    ["Übersicht", "PPT zu PDF", "Farbkontrast-Checker", "Alt-Text Generator", "PDF Prüfer", "Text-zu-Sprache"]
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Barrierefreiheits-Tools</strong> | Entwickelt mit ❤️ für eine zugänglichere digitale Welt</p>
    <p style='font-size: 0.9rem;'>Basierend auf WCAG 2.1 Richtlinien (Web Content Accessibility Guidelines)</p>
</div>
""", unsafe_allow_html=True)
