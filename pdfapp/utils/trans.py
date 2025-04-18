import io, os
from PyPDF2 import PdfReader, PdfWriter
from googletrans import Translator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings

# Font directory
FONTS_PATH = os.path.join(settings.BASE_DIR, 'fonts')

# Register fonts
pdfmetrics.registerFont(TTFont('NotoSans', os.path.join(FONTS_PATH, 'NotoSans-Regular.ttf')))
pdfmetrics.registerFont(TTFont('NotoSansSC', os.path.join(FONTS_PATH, 'NotoSansSC-Regular.ttf')))
pdfmetrics.registerFont(TTFont('NotoSansJP', os.path.join(FONTS_PATH, 'NotoSansJP-Regular.ttf')))
pdfmetrics.registerFont(TTFont('NotoSansDev', os.path.join(FONTS_PATH, 'NotoSansDevanagari-Regular.ttf')))

# Language to font mapping (by base code)
LANG_FONT_MAP = {
    'en': 'NotoSans',
    'fr': 'NotoSans',
    'de': 'NotoSans',
    'ru': 'NotoSans',
    'pt': 'NotoSans',
    'es': 'NotoSans',
    'zh': 'NotoSansSC',
    'ja': 'NotoSansJP',
    'hi': 'NotoSansDev',
    'mr': 'NotoSansDev',
    'bn': 'NotoSansDev',
}

def translate_pdf(input_pdf_file, dest_language):
    translator = Translator()
    reader = PdfReader(input_pdf_file)
    writer = PdfWriter()

    # Normalize language code (e.g., zh-cn → zh)
    lang_code = dest_language.lower()
    if lang_code in ['zh-cn', 'zh']:
        lang_code = 'zh-cn'
        font_key = 'zh'
    elif lang_code in ['ja', 'jp']:
        lang_code = 'ja'
        font_key = 'ja'
    else:
        font_key = lang_code.split('-')[0]

    font_name = LANG_FONT_MAP.get(font_key, 'NotoSans')
    print(f"📝 Using font for language '{lang_code}': {font_name}")

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"📄 Page {i+1} original text: {text[:100]}..." if text else "❌ No text found.")

        if text:
            try:
                translated = translator.translate(text, src="en", dest=lang_code).text
            except Exception as e:
                translated = "[Translation failed]"
                print(f"❌ Translation error: {e}")

            print(f"🌐 Translated (Page {i+1}): {translated[:100]}...")

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            width, height = letter
            margin = 40
            max_width = width - 2 * margin
            font_size = 12
            line_height = font_size * 1.5

            can.setFont(font_name, font_size)
            lines = simpleSplit(translated, font_name, font_size, max_width)
            y = height - margin

            for line in lines:
                if y < margin:
                    can.showPage()
                    can.setFont(font_name, font_size)
                    y = height - margin
                can.drawString(margin, y, line)
                y -= line_height

            can.save()
            packet.seek(0)
            translated_pdf = PdfReader(packet)

            for page_obj in translated_pdf.pages:
                writer.add_page(page_obj)
        else:
            writer.add_page(page)

    output_pdf = io.BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0)
    return output_pdf
