const API_BASE_URL = "http://127.0.0.1:8000";

const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const previewSection = document.getElementById("previewSection");
const originalPreview = document.getElementById("originalPreview");
const resultPreview = document.getElementById("resultPreview");
const resultPlaceholder = document.getElementById("resultPlaceholder");
const deblurBtn = document.getElementById("deblurBtn");
const downloadBtn = document.getElementById("downloadBtn");
const resetBtn = document.getElementById("resetBtn");
const loadingIndicator = document.getElementById("loadingIndicator");
const errorMessage = document.getElementById("errorMessage");

let selectedFile = null;
let resultDownloadUrl = null;

// --- Upload interactions -------------------------------------------------

uploadZone.addEventListener("click", () => fileInput.click());

uploadZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  uploadZone.classList.add("dragover");
});

uploadZone.addEventListener("dragleave", () => {
  uploadZone.classList.remove("dragover");
});

uploadZone.addEventListener("drop", (event) => {
  event.preventDefault();
  uploadZone.classList.remove("dragover");
  const file = event.dataTransfer.files[0];
  if (file) handleFileSelected(file);
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) handleFileSelected(file);
});

function handleFileSelected(file) {
  if (!file.type.startsWith("image/")) {
    showError("Please select an image file.");
    return;
  }

  selectedFile = file;
  hideError();

  const reader = new FileReader();
  reader.onload = (event) => {
    originalPreview.src = event.target.result;
    previewSection.classList.remove("hidden");
    resetResultView();
  };
  reader.readAsDataURL(file);
}

function resetResultView() {
  resultPreview.classList.add("hidden");
  resultPlaceholder.classList.remove("hidden");
  downloadBtn.classList.add("hidden");
  resultDownloadUrl = null;
}

// --- Deblur action ---------------------------------------------------------

deblurBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  hideError();
  loadingIndicator.classList.remove("hidden");
  deblurBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch(`${API_BASE_URL}/deblur`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Deblurring failed. Please try again.");
    }

    const data = await response.json();
    resultDownloadUrl = `${API_BASE_URL}${data.download_url}`;

    resultPreview.src = `${resultDownloadUrl}?t=${Date.now()}`;
    resultPreview.classList.remove("hidden");
    resultPlaceholder.classList.add("hidden");
    downloadBtn.classList.remove("hidden");
  } catch (error) {
    showError(error.message || "Something went wrong. Is the backend server running?");
  } finally {
    loadingIndicator.classList.add("hidden");
    deblurBtn.disabled = false;
  }
});

// --- Download action ---------------------------------------------------------

downloadBtn.addEventListener("click", () => {
  if (!resultDownloadUrl) return;
  const link = document.createElement("a");
  link.href = resultDownloadUrl;
  link.download = "deblurred_result.png";
  link.click();
});

// --- Reset ---------------------------------------------------------

resetBtn.addEventListener("click", () => {
  selectedFile = null;
  resultDownloadUrl = null;
  fileInput.value = "";
  previewSection.classList.add("hidden");
  hideError();
});

// --- Helpers ---------------------------------------------------------

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.remove("hidden");
}

function hideError() {
  errorMessage.classList.add("hidden");
}