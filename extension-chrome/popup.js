const extApi = typeof browser !== "undefined" ? browser : chrome;

const RISK_EMOJI = {
  CRITIQUE: "🔴",
  ÉLEVÉ:    "🟠",
  MOYEN:    "🟡",
  FAIBLE:   "🟢",
  HIGH:     "🔴",
  MEDIUM:   "🟡",
  LOW:      "🟢",
};

document.getElementById("scanBtn").addEventListener("click", () => {
  const input = document.getElementById("textInput").value.trim();
  if (!input) return;

  const btn         = document.getElementById("scanBtn");
  const resultDiv   = document.getElementById("result");
  const badgeDiv    = document.getElementById("scoreBadge");
  const expDiv      = document.getElementById("explanation");
  const findingsDiv = document.getElementById("findingsContainer");

  btn.innerText = "⏳ Analyse en cours...";
  resultDiv.style.display = "none";

  const isUrl = input.startsWith("http://") || input.startsWith("https://") || input.includes(".com") || input.includes(".ci") || input.includes(".xyz");
  const msgType = isUrl ? "ANALYZE_URL" : "ANALYZE_TEXT";
  const payload = isUrl ? { type: msgType, url: input } : { type: msgType, text: input };

  extApi.runtime.sendMessage(payload, (response) => {
    btn.innerText = "🔍 Scanner l'Élément";

    if (extApi.runtime.lastError) {
      console.error("[0xSentinelle] Erreur runtime:", extApi.runtime.lastError.message);
      alert("Erreur de connexion — Backend non disponible ou extension non chargée.");
      return;
    }

    if (!response || !response.success) {
      alert("Erreur de connexion au serveur local 0xSentinelle (Backend FastAPI non disponible sur port 8000).");
      return;
    }

    const data = response.data;
    resultDiv.style.display = "block";

    // Score badge — compatibilité FR et EN
    const levelRaw  = data.level || "INCONNU";
    const emoji     = data.level_emoji || RISK_EMOJI[levelRaw.toUpperCase()] || "⚪";
    const score     = data.score ?? "?";
    badgeDiv.innerText = `${emoji} ${score}/100 — RISQUE ${levelRaw}`;
    badgeDiv.className = `badge badge-${levelRaw.toLowerCase()}`;

    // Explication IA
    expDiv.innerText = data.explanation || "Aucune explication disponible.";

    // Trouvailles techniques (URL ou Scraper)
    if (data.technical_findings && data.technical_findings.length > 0) {
      findingsDiv.innerHTML =
        `<strong>🔎 Trouvailles techniques :</strong><ul>` +
        data.technical_findings.map(f => `<li>${f}</li>`).join("") +
        `</ul>`;
    } else {
      findingsDiv.innerHTML = "";
    }

    // Recommandations si présentes
    if (data.recommendations && data.recommendations.length > 0) {
      findingsDiv.innerHTML +=
        `<strong>🛡 Recommandations :</strong><ul>` +
        data.recommendations.slice(0, 3).map(r => `<li>${r}</li>`).join("") +
        `</ul>`;
    }
  });
});

// Sanity check au chargement
document.addEventListener("DOMContentLoaded", () => {
  fetch("http://localhost:8000/health")
    .then(res => res.json())
    .then(data => {
      const statusEl = document.getElementById("backendStatus");
      if (statusEl) {
        statusEl.textContent = "✅ Backend connecté";
        statusEl.style.color = "#22c55e";
      }
    })
    .catch(() => {
      const statusEl = document.getElementById("backendStatus");
      if (statusEl) {
        statusEl.textContent = "❌ Backend hors ligne";
        statusEl.style.color = "#ef4444";
      }
    });
});
