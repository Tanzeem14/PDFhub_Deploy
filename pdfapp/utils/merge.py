from pypdf import PdfWriter
import os

def merge_pdfs(pdf_paths, output_path):
    """
    Merge multiple PDF files from different locations into a single PDF.
    
    Args:
        pdf_paths (list): List of absolute file paths of PDFs.
        output_path (str): Absolute path to save the merged PDF.
    
    Returns:
        str: Path of the merged PDF.
    """
    writer = PdfWriter()

    for pdf in pdf_paths:
        if os.path.exists(pdf):  # ✅ Check if the file exists
            writer.append(pdf)
        else:
            print(f"⚠️ File not found: {pdf}")

    writer.write(output_path)
    writer.close()
    return output_path
