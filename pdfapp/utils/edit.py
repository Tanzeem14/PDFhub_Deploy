from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
import os
from django.views.decorators.csrf import csrf_exempt


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


@csrf_exempt
def save_pdf(request):
    """
    Handles saving the updated PDF file and returns the download URL.
    """
    try:
        if request.method == 'POST' and request.FILES.get('pdf'):
            pdf_file = request.FILES['pdf']

            # Sanitize the file name to avoid issues with spaces or special characters
            original_name = os.path.splitext(pdf_file.name)[0]
            extension = os.path.splitext(pdf_file.name)[1]
            sanitized_name = original_name.replace(" ", "_") + extension

            # Save the file in the 'edited' directory
            save_path = os.path.join(settings.MEDIA_ROOT, 'edited', sanitized_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            # Return the download URL
            download_url = settings.MEDIA_URL + 'edited/' + sanitized_name
            print(f"File saved at: {save_path}")  # Debugging
            print(f"Download URL: {download_url}")  # Debugging
            return JsonResponse({'success': True, 'download_url': download_url})

        return JsonResponse({'success': False, 'error': 'Invalid request'})
    except Exception as e:
        print(f"Error saving PDF: {e}")  # Debugging
        return JsonResponse({'success': False, 'error': str(e)})


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