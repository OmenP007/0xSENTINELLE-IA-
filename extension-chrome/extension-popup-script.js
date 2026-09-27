document.getElementById("scanBtn").addEventListener("click", () => {
  const input = document.getElementById("textInput").value.trim();
  if (!input) return;

  const btn = document.getElementById("scanBtn");
  const resultDiv = document.getElementById("result");
  const badgeDiv = document.getElementById("scoreBadge");
  const expDiv = document.getElementById("explanation");
  const findingsDiv = document.getElementById("findingsContainer");

  btn.innerText = "⏳ Analyse en cours...";

  const isUrl = input.startsWith("http://") || input.startsWith("https://") || input.includes(".com") || input.includes(".ci") || input.includes(".xyz");
  const msgType = isUrl ? "ANALYZE_URL" : "ANALYZE_TEXT";
  const payload = isUrl ? { type: msgType, url: input } : { type: msgType, text: input };

  chrome.runtime.sendMessage(payload, (response) => {
    btn.innerText = "🔍 Scanner l'Élément";

    if (!response || !response.success) {
      alert("Erreur de connexion au serveur local 0xSentinelle (Backend FastAPI non disponible).");
      return;
    }

    const data = response.data;
    resultDiv.style.display = "block";

    // Set badge
    badgeDiv.innerText = `${data.level_emoji} ${data.score}/100 — RISQUE ${data.level}`;
    badgeDiv.className = `badge badge-${data.level.toLowerCase()}`;

    // Explanation
    expDiv.innerText = data.explanation;

    // Findings if URL
    if (data.technical_findings && data.technical_findings.length > 0) {
      findingsDiv.innerHTML = `<strong>Trouvailles techniques :</strong><ul>` +
        data.technical_findings.map(f => `<li>${f}</li>`).join("") +
        `</ul>`;
    } else {
      findingsDiv.innerHTML = "";
    }
  });
});
