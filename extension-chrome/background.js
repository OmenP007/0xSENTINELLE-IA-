// ─── Service Worker 0xSentinelle Shield (Firefox & Chrome/Brave) ────────────
const extApi = typeof browser !== "undefined" ? browser : chrome;
const BACKEND_URL = "http://localhost:8000";

// Reçoit les demandes d'analyse du Content Script ou de la Popup
extApi.runtime.onMessage.addListener((request, sender, sendResponse) => {

  if (request.type === "ANALYZE_TEXT") {
    fetch(`${BACKEND_URL}/analyze/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: request.text,
        claimed_brand: request.claimed_brand || null,
      }),
    })
      .then((res) => res.json())
      .then((data) => sendResponse({ success: true, data }))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true; // Asynchrone
  }

  if (request.type === "ANALYZE_URL") {
    fetch(`${BACKEND_URL}/analyze/url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: request.url,
        claimed_brand: request.claimed_brand || null,
      }),
    })
      .then((res) => res.json())
      .then((data) => sendResponse({ success: true, data }))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true; // Asynchrone
  if (request.type === "ANALYZE_CONVERSATION") {
    fetch(`${BACKEND_URL}/analyze/conversation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: request.transcript,
        claimed_brand: request.claimed_brand || null,
      }),
    })
      .then((res) => res.json())
      .then((data) => sendResponse({ success: true, data }))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true; // Asynchrone
  }
});

