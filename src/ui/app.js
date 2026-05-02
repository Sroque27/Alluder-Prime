/* -------------------------------------------------------
   app.js
   -------
   Handles:
   - Sending text, PDF, or URL to the backend
   - Receiving annotations
   - Updating the UI
   - Triggering highlight + bubble rendering
------------------------------------------------------- */

/* DOM elements */
const textInput = document.getElementById("text-input");
const pdfInput = document.getElementById("pdf-input");
const urlInput = document.getElementById("url-input");

const analyzeTextBtn = document.getElementById("analyze-text-btn");
const analyzePdfBtn = document.getElementById("analyze-pdf-btn");
const analyzeUrlBtn = document.getElementById("analyze-url-btn");

const textDisplay = document.getElementById("text-display");
const insightDisplay = document.getElementById("insight-display");


/* -------------------------------------------------------
   Helper: Send POST request with form data
------------------------------------------------------- */
async function postFormData(url, formData) {
    const response = await fetch(url, {
        method: "POST",
        body: formData
    });
    return response.json();
}


/* -------------------------------------------------------
   Analyze raw text
------------------------------------------------------- */
analyzeTextBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) return;

    // Clear old bubbles
    window.clearBubbles();

    const formData = new FormData();
    formData.append("text", text);

    const result = await postFormData("/analyze/text", formData);

    // Display original text
    textDisplay.textContent = result.original_text;

    // Display raw JSON (optional)
    insightDisplay.textContent = JSON.stringify(result.annotations, null, 2);

    // Highlight spans + enable bubbles
    window.highlightAnnotations(result.original_text, result.annotations);
});


/* -------------------------------------------------------
   Analyze PDF upload
------------------------------------------------------- */
analyzePdfBtn.addEventListener("click", async () => {
    if (!pdfInput.files.length) return;

    // Clear old bubbles
    window.clearBubbles();

    const formData = new FormData();
    formData.append("file", pdfInput.files[0]);

    const result = await postFormData("/analyze/pdf", formData);

    textDisplay.textContent = result.original_text;
    insightDisplay.textContent = JSON.stringify(result.annotations, null, 2);

    window.highlightAnnotations(result.original_text, result.annotations);
});


/* -------------------------------------------------------
   Analyze URL
------------------------------------------------------- */
analyzeUrlBtn.addEventListener("click", async () => {
    const url = urlInput.value.trim();
    if (!url) return;

    // Clear old bubbles
    window.clearBubbles();

    const formData = new FormData();
    formData.append("url", url);

    const result = await postFormData("/analyze/url", formData);

    textDisplay.textContent = result.original_text;
    insightDisplay.textContent = JSON.stringify(result.annotations, null, 2);

    window.highlightAnnotations(result.original_text, result.annotations);
});
