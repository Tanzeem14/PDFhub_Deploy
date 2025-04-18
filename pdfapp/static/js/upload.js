document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.getElementById('pdf_file');
  const previewContainer = document.getElementById('pdfPreview');

  if (fileInput && previewContainer) {
    fileInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file && file.type === 'application/pdf') {
        const fileURL = URL.createObjectURL(file);
        previewContainer.innerHTML = `
          <embed src="${fileURL}" type="application/pdf" width="100%" height="500px" />
        `;
      } else {
        previewContainer.innerHTML = '<p>Please select a valid PDF file to preview.</p>';
      }
    });
  }
});
