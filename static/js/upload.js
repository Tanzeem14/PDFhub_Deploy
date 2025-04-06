console.log("convert-upload.js loaded successfully!");

document.getElementById("pdfInput").addEventListener("change", function (event) {
    const files = event.target.files;

    if (files.length > 1) {
        alert("Only one PDF file can be converted at a time.");
        
        // Reset file input to allow reselection
        event.target.value = "";  
        return;
    }

    if (files.length === 0) {
        alert("Please upload a valid PDF file.");
        return;
    }

    // Get elements
    const loader = document.getElementById("loading");
    const previewContainer = document.getElementById("pdfPreviewContainer");
    const fileUploadSection = document.querySelector(".container"); // Hide the upload section
    const fileLabel = document.querySelector(".custom-file-upload"); // Hide the "Choose Files" button

    // Hide upload UI & Show loader
    fileUploadSection.style.display = "none";
    fileLabel.style.display = "none";
    loader.style.display = "flex";
    previewContainer.innerHTML = ""; // Clear previous preview

    const file = files[0];
    const fileReader = new FileReader();
    fileReader.readAsArrayBuffer(file);

    fileReader.onload = function () {
        const pdfData = new Uint8Array(fileReader.result);

        setTimeout(() => {
            console.log("Processing PDF...");

            pdfjsLib.getDocument({ data: pdfData }).promise.then(pdf => {
                pdf.getPage(1).then(page => {
                    const scale = 1.0;
                    const viewport = page.getViewport({ scale });
                    const canvas = document.createElement("canvas");
                    const context = canvas.getContext("2d");

                    canvas.width = viewport.width;
                    canvas.height = viewport.height;

                    previewContainer.appendChild(canvas);

                    page.render({ canvasContext: context, viewport }).promise.then(() => {
                        console.log("First page displayed.");
                        setTimeout(() => {
                            loader.style.display = "none"; // Hide loader after rendering
                        }, 500);
                    });
                });
            }).catch(err => {
                console.error("Error loading PDF:", err);
                loader.style.display = "none"; // Hide loader on error
                fileUploadSection.style.display = "block"; // Show upload UI again
                fileLabel.style.display = "block";
            });
        }, 1000);
    };
});
