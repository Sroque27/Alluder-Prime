/* -------------------------------------------------------
   bubbles.js
   -----------
   Handles:
   - Highlighting annotated spans in the text
   - Creating interactive insight bubbles
   - Rendering background knowledge, dates, abbreviations, etc.
------------------------------------------------------- */

/* The container where bubbles appear */
const bubbleContainer = document.getElementById("bubble-container");

/* -------------------------------------------------------
   Clear all existing bubbles
------------------------------------------------------- */
function clearBubbles() {
    bubbleContainer.innerHTML = "";
}

/* -------------------------------------------------------
   Create a single bubble
------------------------------------------------------- */
function createBubble(title, content) {
    const bubble = document.createElement("div");
    bubble.className = "bubble";

    const heading = document.createElement("h4");
    heading.textContent = title;

    const paragraph = document.createElement("p");
    paragraph.textContent = content;

    bubble.appendChild(heading);
    bubble.appendChild(paragraph);

    bubbleContainer.appendChild(bubble);
}

/* -------------------------------------------------------
   Highlight spans in the displayed text
   and attach event listeners for bubbles
------------------------------------------------------- */
function highlightAnnotations(originalText, annotations) {
    const display = document.getElementById("text-display");
    let html = originalText;

    // We will wrap each annotated span in a <span class="highlight">
    // This is a simple version — later you can refine span matching.
    const spansToHighlight = [];

    // Collect all entity-like annotations
    if (annotations.entities) {
        annotations.entities.forEach(ent => {
            spansToHighlight.push({
                text: ent.text,
                type: ent.label,
                background: ent.background || null
            });
        });
    }

    if (annotations.date_periods) {
        annotations.date_periods.forEach(dp => {
            spansToHighlight.push({
                text: dp.text,
                type: "date_period",
                background: null
            });
        });
    }

    if (annotations.abbreviations) {
        annotations.abbreviations.forEach(ab => {
            spansToHighlight.push({
                text: ab.text,
                type: "abbreviation",
                background: null
            });
        });
    }

    if (annotations.quotations) {
        annotations.quotations.forEach(q => {
            spansToHighlight.push({
                text: q.text,
                type: "quotation",
                background: null
            });
        });
    }

    // Replace each span in the text with a highlighted version
    spansToHighlight.forEach(span => {
        const safeText = span.text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); // escape regex
        const regex = new RegExp(`\\b${safeText}\\b`, "g");

        html = html.replace(
            regex,
            `<span class="highlight" data-type="${span.type}" data-bg='${JSON.stringify(span.background)}'>${span.text}</span>`
        );
    });

    display.innerHTML = html;

    // Attach event listeners to highlighted spans
    const highlights = document.querySelectorAll(".highlight");

    highlights.forEach(span => {
        span.addEventListener("click", () => {
            clearBubbles();

            const type = span.getAttribute("data-type");
            const bg = JSON.parse(span.getAttribute("data-bg"));

            // Title for the bubble
            let title = `${span.textContent} (${type})`;

            // Content for the bubble
            let content = "";

            if (bg && bg.wikipedia) {
                content += bg.wikipedia;
            } else if (bg && bg.wikidata) {
                content += bg.wikidata;
            } else {
                content += "No additional background information available.";
            }

            createBubble(title, content);
        });
    });
}

/* -------------------------------------------------------
   Export function for app.js
------------------------------------------------------- */
window.highlightAnnotations = highlightAnnotations;
window.clearBubbles = clearBubbles;
