import PyPDF2 
from django.conf import settings
import os
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

# ✅ Load the summarizer ONCE when this module is imported
# summarizer = pipeline(
#     "summarization",
#     model="sshleifer/distilbart-cnn-12-6",
#     device=-1  # CPU only
# )
summarizer = pipeline("summarization", model="Falconsai/text_summarization")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""  # fallback if page has no text
            return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise

def summarize_pdf(pdf_file):
    """Summarize the content of a PDF file"""
    temp_path = None
    try:
        # Save uploaded file temporarily
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, pdf_file.name)
        
        with open(temp_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        # Extract text
        text = extract_text_from_pdf(temp_path)

        if not text.strip():
            raise ValueError("No text found in PDF.")

        # Split into chunks to fit the model input size
        max_chunk_length = 1024
        chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        summary = ""

        for chunk in chunks:
            result = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
            summary += result[0]['summary_text'] + "\n\n"
        
        return summary.strip()

    except Exception as e:
        logger.error(f"Error summarizing PDF: {e}")
        raise
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

