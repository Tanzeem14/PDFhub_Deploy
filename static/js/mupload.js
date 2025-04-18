
document.getElementById("pdfInput").addEventListener("change", function (event) {
    const files = event.target.files;

    if (files.length === 0) {
        alert("Please upload at least one PDF file.");
        return;
    }

    const loader = document.getElementById("loading");
    const previewContainer = document.getElementById("pdfPreviewContainer");
    const fileUploadSection = document.querySelector(".container");
    const fileLabel = document.querySelector(".custom-file-upload");

    fileUploadSection.style.display = "none";
    fileLabel.style.display = "none";
    loader.style.display = "flex";
    previewContainer.innerHTML = "";

    let processedFiles = 0;

    Array.from(files).forEach((file, index) => {
        const fileReader = new FileReader();
        fileReader.readAsArrayBuffer(file);

        fileReader.onload = function () {
            const pdfData = new Uint8Array(fileReader.result);

            setTimeout(() => {
                console.log(`Processing file ${index + 1}: ${file.name}`);

                pdfjsLib.getDocument({ data: pdfData }).promise.then(pdf => {
                    pdf.getPage(1).then(page => {
                        const scale = 0.8;
                        const viewport = page.getViewport({ scale });
                        const canvas = document.createElement("canvas");
                        const context = canvas.getContext("2d");

                        canvas.width = viewport.width;
                        canvas.height = viewport.height;

                        previewContainer.appendChild(canvas);

                        page.render({ canvasContext: context, viewport }).promise.then(() => {
                            console.log(`PDF preview displayed for file ${index + 1}`);
                            processedFiles++;

                            if (processedFiles === files.length) {
                                setTimeout(() => {
                                    loader.style.display = "none";
                                    console.log("All PDFs processed, hiding loader.");
                                }, 300);
                            }
                        });

                    });
                }).catch(err => {
                    console.error("Error loading PDF:", err);
                    loader.style.display = "none";
                    fileUploadSection.style.display = "block";
                    fileLabel.style.display = "block";
                });

            }, 1000);
        };
    });
});

document.getElementById("mergeBtn").addEventListener("click", function (e) {
    e.preventDefault(); // Prevent immediate form submit

    // Hide upload section and show loader
    document.getElementById("uploadSection").style.display = "none";
    document.getElementById("loading").style.display = "flex";

    // Submit the form after a small delay
    setTimeout(() => {
        document.getElementById("mergeForm").submit();
    }, 500);
});
