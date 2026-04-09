const form = document.getElementById("predictForm");
const submitBtn = document.getElementById("submitBtn");
const clearBtn = document.getElementById("clearBtn");
const fileInput = document.getElementById("image");
const dropZone = document.getElementById("dropZone");
const fileName = document.getElementById("fileName");
const previewWrap = document.getElementById("previewWrap");
const previewImage = document.getElementById("previewImage");

function updatePreview(selectedFile) {
    if (!fileName || !previewWrap || !previewImage) {
        return;
    }

    if (!selectedFile) {
        fileName.textContent = "No file selected";
        previewWrap.hidden = true;
        previewImage.removeAttribute("src");
        return;
    }

    fileName.textContent = selectedFile.name;
    previewWrap.hidden = false;
    previewImage.src = URL.createObjectURL(selectedFile);
}

if (fileInput) {
    fileInput.addEventListener("change", () => {
        updatePreview(fileInput.files && fileInput.files[0] ? fileInput.files[0] : null);
    });
}

if (dropZone && fileInput) {
    dropZone.addEventListener("click", () => fileInput.click());
    dropZone.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            fileInput.click();
        }
    });

    ["dragenter", "dragover"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.add("is-dragover");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.remove("is-dragover");
        });
    });

    dropZone.addEventListener("drop", (event) => {
        const droppedFiles = event.dataTransfer ? event.dataTransfer.files : null;
        if (!droppedFiles || droppedFiles.length === 0) {
            return;
        }

        const transfer = new DataTransfer();
        transfer.items.add(droppedFiles[0]);
        fileInput.files = transfer.files;
        updatePreview(droppedFiles[0]);
    });
}

if (form && submitBtn) {
    form.addEventListener("submit", () => {
        submitBtn.disabled = true;
        submitBtn.textContent = "Running...";
    });
}

if (clearBtn && form) {
    clearBtn.addEventListener("click", () => {
        const url = new URL(window.location.href);
        url.search = "";
        window.location.href = url.toString();
    });
}
