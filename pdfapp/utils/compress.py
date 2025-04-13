import os
import subprocess
from django.conf import settings
import uuid

def compress_pdf(uploaded_file, quality='/ebook'):
    """
    Compress a PDF file using Ghostscript.

    Args:
        uploaded_file: The uploaded PDF file.
        quality: The compression quality (e.g., '/screen', '/ebook', '/printer', '/prepress').

    Returns:
        str: Path to the compressed PDF file.
    """
    # Ensure the temp directory exists
    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Generate unique temp input file path to avoid name collision
    temp_input_filename = f"temp_{uuid.uuid4().hex}_{uploaded_file.name}"
    temp_input_path = os.path.join(temp_dir, temp_input_filename)

    # Save the uploaded file temporarily
    with open(temp_input_path, "wb") as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)

    # Prepare output filename: compressed_<originalname>.pdf
    original_name = os.path.splitext(uploaded_file.name)[0]  # 'hello' from 'hello.pdf'
    compressed_filename = f"compressed_{original_name}.pdf"
    output_path = os.path.join(temp_dir, compressed_filename)

    # Validate quality setting
    valid_qualities = ["/screen", "/ebook", "/printer", "/prepress", "/default"]
    if quality not in valid_qualities:
        raise ValueError(f"Invalid quality setting: {quality}. Choose from {valid_qualities}.")

    # If compressed file already exists, delete it
    if os.path.exists(output_path):
        os.remove(output_path)

    # Ghostscript command (no extra quotes)
    gs_command = [
        r"C:\Program Files\gs\gs10.05.0\bin\gswin64c.exe",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={quality}",
        "-dNOPAUSE",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        temp_input_path,
    ]

    try:
        print("Running Ghostscript command:", " ".join(gs_command))
        result = subprocess.run(gs_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Ghostscript output:", result.stdout.decode('utf-8'))
        print("Ghostscript error (if any):", result.stderr.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(f"Ghostscript error output: {e.stderr.decode('utf-8')}")
        raise Exception(f"Ghostscript compression failed: {e}")
    except FileNotFoundError:
        raise Exception("Ghostscript executable not found. Ensure Ghostscript is installed and in PATH.")
    finally:
        # Clean up temp input file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

    return output_path
