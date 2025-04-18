from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
import os
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

import shutil
import tempfile
import subprocess

@csrf_exempt
def save_pdf(request):
    """
    Handles saving the updated PDF file and annotation (XFDF) and returns the download + editor URLs.
    Applies XFDF annotations to original PDF and saves edited PDF separately.
    """
    try:
        if request.method == 'POST' and request.FILES.get('xfdf') and request.POST.get('pdf_path'):
            xfdf_file = request.FILES['xfdf']
            original_pdf_path = request.POST.get('pdf_path')

            # Sanitize the file name (from XFDF file name, assume same as PDF)
            original_name = os.path.splitext(xfdf_file.name)[0]
            sanitized_name = original_name.replace(" ", "_")
            pdf_filename = sanitized_name + '.pdf'
            xfdf_filename = sanitized_name + '.xfdf'

            # Save XFDF file
            xfdf_path = os.path.join(settings.MEDIA_ROOT, 'edited', xfdf_filename)
            os.makedirs(os.path.dirname(xfdf_path), exist_ok=True)

            with open(xfdf_path, 'wb') as f:
                for chunk in xfdf_file.chunks():
                    f.write(chunk)

            # Paths
            original_pdf_full_path = os.path.join(settings.MEDIA_ROOT, original_pdf_path)
            edited_pdf_path = os.path.join(settings.MEDIA_ROOT, 'edited', pdf_filename)

            # Apply XFDF annotations to original PDF to create edited PDF
            try:
                # Use saved XFDF file path instead of temp file
                pdftk_path = r'D:\\PDFAPPLIBRARY\\PDFtk\\bin\\pdftk.exe'
                cmd = [
                    pdftk_path,
                    original_pdf_full_path,
                    'fill_form',
                    xfdf_path,
                    'output',
                    edited_pdf_path,
                    'flatten'
                ]
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"pdftk stdout: {result.stdout}")
                print(f"pdftk stderr: {result.stderr}")

            except subprocess.CalledProcessError as e:
                print(f"pdftk command failed with return code {e.returncode}")
                print(f"pdftk stdout: {e.stdout}")
                print(f"pdftk stderr: {e.stderr}")
                # Fallback: copy original PDF to edited folder without changes
                shutil.copyfile(original_pdf_full_path, edited_pdf_path)
            except Exception as e:
                print(f"Error applying XFDF to PDF: {e}")
                shutil.copyfile(original_pdf_full_path, edited_pdf_path)

            # Return URLs for edited PDF and editor
            download_url = settings.MEDIA_URL + 'edited/' + pdf_filename
            editor_url = reverse('editor_page', kwargs={'pdf_path': 'edited/' + pdf_filename})

            print(f"Edited PDF saved at: {edited_pdf_path}")
            print(f"Redirecting to: {editor_url}")

            xfdf_download_url = settings.MEDIA_URL + 'edited/' + xfdf_filename

            return JsonResponse({
                'success': True,
                'download_url': download_url,
                'xfdf_download_url': xfdf_download_url,
                'editor_url': editor_url
            })

        return JsonResponse({'success': False, 'error': 'No XFDF file or pdf_path received'})
    except Exception as e:
        print(f"Error saving PDF/XFDF: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

def open_editor(request):
    """
    Handles the upload of a PDF file and redirects to the editor page.
    """
    if request.method == 'POST' and request.FILES.get('pdf_files'):
        pdf_file = request.FILES['pdf_files']
        fs = FileSystemStorage()

        # Save the uploaded file to the media folder
        filename = fs.save(pdf_file.name, pdf_file)
        file_url = fs.url(filename)  # Generate the URL for the uploaded file
        print(f"File URL: {file_url}")  # Debugging

        # Redirect to the editor page with the file path
        return redirect('editor_page', pdf_path=filename)

    return render(request, 'edit.html')

def download_pdf(request, pdf_path):
    """
    Handles downloading a PDF file from the server.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return response
    else:
        return HttpResponseNotFound("File not found.")
