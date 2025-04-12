# from pypdf import PdfWriter
# import os

# def merge_pdfs(pdf_paths, output_path):
#     """
#     Merge multiple PDF files from different locations into a single PDF.
    
#     Args:
#         pdf_paths (list): List of absolute file paths of PDFs.
#         output_path (str): Absolute path to save the merged PDF.
    
#     Returns:
#         str: Path of the merged PDF.
#     """
#     writer = PdfWriter()

#     for pdf in pdf_paths:
#         if os.path.exists(pdf):  # ✅ Check if the file exists
#             writer.append(pdf)
#         else:
#             print(f"⚠️ File not found: {pdf}")

#     writer.write(output_path)
#     writer.close()
#     return output_path
import os
import PyPDF2
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

def merge_pdfs(uploaded_files):
    if len(uploaded_files) < 2:
        return False, "Please upload at least 2 PDFs to merge."

    merger = PyPDF2.PdfMerger()
    temp_files = []

    try:
        for file in uploaded_files:
            file_path = default_storage.save(f"temp/{file.name}", ContentFile(file.read()))
            temp_files.append(file_path)

            with default_storage.open(file_path, "rb") as pdf_file:
                merger.append(pdf_file)

        merged_pdf_path = os.path.join(settings.MEDIA_ROOT, "merged_output.pdf")

        with open(merged_pdf_path, "wb") as output_file:
            merger.write(output_file)

        merger.close()
        return True, "PDFs Merged Successfully!"

    finally:
        for file in temp_files:
            default_storage.delete(file)
