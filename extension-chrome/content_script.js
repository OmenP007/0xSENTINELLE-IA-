// ─── 0xSentinelle Shield Content Script (Firefox & Chrome/Brave) ────────────
const extApi = typeof browser !== "undefined" ? browser : chrome;

console.log("[0xSentinelle Shield] Content Script activé");

// SVG Icones vectorielles pour l'interface utilisateur
const ICONS = {
  shield: `<svg class="sentinelle-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
  alert: `<svg class="sentinelle-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  store: `<svg class="sentinelle-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>`,
  close: `<svg class="sentinelle-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
  check: `<svg class="sentinelle-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
  cpu: `<svg class="sentinelle-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="16" height="16" x="4" y="4" rx="2"/><path d="M9 9h6v6H9z"/><path d="M15 2v2M9 2v2M15 20v2M9 20v2M2 15h2M2 9h2M20 15h2M20 9h2"/></svg>`,
  file: `<svg class="sentinelle-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>`,
  zap: `<svg class="sentinelle-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`
};

// Injecter la bannière de notification d'analyse dans la page
function showRiskBanner(targetElement, result) {
  const existing = targetElement.querySelector(".sentinelle-risk-banner");
  if (existing) existing.remove();

  const isHighRisk = result.score >= 60;
  const banner = document.createElement("div");
  banner.className = `sentinelle-risk-banner ${isHighRisk ? "high-risk" : "low-risk"}`;

  const findingsList = result.technical_findings
    ? result.technical_findings.map((f) => `<li>${f}</li>`).join("")
    : "";

  const iconToUse = isHighRisk ? ICONS.alert : ICONS.check;

  banner.innerHTML = `
    <div class="sentinelle-banner-header">
      <span class="sentinelle-badge">${iconToUse} Score ${result.score}/100 — RISQUE ${result.level}</span>
      <span class="sentinelle-close">${ICONS.close}</span>
    </div>
    <div class="sentinelle-banner-body">
      <p><strong>${ICONS.cpu} Synthèse IA :</strong> ${result.explanation}</p>
      ${findingsList ? `<ul class="sentinelle-findings">${findingsList}</ul>` : ""}
      <p><strong>${ICONS.shield} Recommandation :</strong> ${result.recommendations ? result.recommendations[0] : ""}</p>
    </div>
  `;

  banner.querySelector(".sentinelle-close").onclick = () => banner.remove();
  targetElement.appendChild(banner);
}

// Bouton d'analyse flottant pour les bulles de discussion WhatsApp / FB
function attachScanButtons() {
  const waMessages = document.querySelectorAll(".message-in, .message-out");
  waMessages.forEach((msg) => {
    if (msg.dataset.sentinelleProcessed) return;
    msg.dataset.sentinelleProcessed = "true";

    const textEl = msg.querySelector(".selectable-text");
    if (!textEl) return;

    const text = textEl.innerText;
    if (!text || text.length < 5) return;

    const btn = document.createElement("button");
    btn.className = "sentinelle-scan-btn";
    btn.innerHTML = `${ICONS.shield} Scan IA`;
    btn.title = "Analyser avec 0xSentinelle IA (Détection arnaque / broutage)";

    btn.onclick = (e) => {
      e.stopPropagation();
      btn.innerHTML = `⏳ Scan...`;
      extApi.runtime.sendMessage(
        { type: "ANALYZE_TEXT", text: text },
        (response) => {
          btn.innerHTML = `${ICONS.shield} Scan IA`;
          if (response && response.success) {
            showRiskBanner(msg, response.data);
          } else {
            alert("Erreur de connexion au serveur 0xSentinelle.");
          }
        }
      );
    };

    msg.style.position = "relative";
    msg.appendChild(btn);
  });

  // Liens suspects trouvés sur la page (WhatsApp & Facebook)
  const links = document.querySelectorAll("a[href^='http']");
  links.forEach((link) => {
    if (link.dataset.sentinelleLinkProcessed) return;
    link.dataset.sentinelleLinkProcessed = "true";

    const href = link.href;

    if (
      href.includes(".xyz") ||
      href.includes("kdo") ||
      href.includes("orange-money") ||
      href.includes("mtn-ci")
    ) {
      link.classList.add("sentinelle-suspicious-link");
      link.title = "Lien potentiellement suspect - Analyser avec 0xSentinelle";

      const warnIcon = document.createElement("span");
      warnIcon.className = "sentinelle-link-badge";
      warnIcon.innerHTML = ` ${ICONS.alert} [Lien Suspect]`;
      warnIcon.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        extApi.runtime.sendMessage(
          { type: "ANALYZE_URL", url: href },
          (res) => {
            if (res && res.success) {
              alert(
                `ANALYSE DE L'URL :\n` +
                `Domaine : ${res.data.domain}\n` +
                `Score de risque : ${res.data.score}/100 (${res.data.level})\n` +
                `Explication : ${res.data.explanation}`
              );
            }
          }
        );
      };
      link.appendChild(warnIcon);
    }
  });
}

// Modal d'analyse de conversation complète
function showFullChatModal(result) {
  const existing = document.querySelector(".sentinelle-modal-overlay");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.className = "sentinelle-modal-overlay";

  const triggersHtml = result.psychological_triggers
    ? result.psychological_triggers.map(t => `<li><strong>${t.name} :</strong> ${t.description}</li>`).join("")
    : "";

  const recsHtml = result.recommendations
    ? result.recommendations.map(r => `<li>${r}</li>`).join("")
    : "";

  const isHigh = result.score >= 60;
  const mainIcon = isHigh ? ICONS.alert : ICONS.check;

  modal.innerHTML = `
    <div class="sentinelle-modal-content">
      <div class="sentinelle-modal-header">
        <h3>${ICONS.shield} Diagnostic Global 0xSentinelle — Conversation Entière</h3>
        <span class="sentinelle-modal-close">${ICONS.close}</span>
      </div>
      <div class="sentinelle-modal-body">
        <div class="sentinelle-score-box ${isHigh ? 'high' : 'low'}">
          ${mainIcon} <strong>Score de Risque : ${result.score}/100 — ${result.level}</strong>
          <span style="display:block; font-size:11px; margin-top:2px;">Type : ${result.scam_type}</span>
        </div>
        
        <p><strong>${ICONS.cpu} Synthèse de l'Agent IA :</strong></p>
        <p class="sentinelle-modal-text">${result.explanation}</p>

        ${triggersHtml ? `<p><strong>${ICONS.zap} Pièges & Déclencheurs Psychologiques :</strong></p><ul>${triggersHtml}</ul>` : ""}

        <p><strong>${ICONS.shield} Recommandations de Sécurité :</strong></p>
        <ul>${recsHtml}</ul>

        ${result.official_report ? `<div class="sentinelle-report-box"><strong>${ICONS.file} Modèle de Signalement Officiel (ARTCI / PLCC) :</strong><br>${result.official_report}</div>` : ""}
      </div>
    </div>
  `;

  modal.querySelector(".sentinelle-modal-close").onclick = () => modal.remove();
  modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
  document.body.appendChild(modal);
}

// Extraction et analyse de la conversation entière (WhatsApp Web / Facebook)
function extractFullChatTranscript() {
  const messages = document.querySelectorAll(".message-in, .message-out, div[role='row']");
  let transcriptLines = [];

  messages.forEach((msg) => {
    const textEl = msg.querySelector(".selectable-text, span.dir-ltr");
    if (!textEl) return;
    const text = textEl.innerText.trim();
    if (!text) return;

    const isOut = msg.classList.contains("message-out");
    const sender = isOut ? "Moi" : "Correspondant";
    transcriptLines.push(`${sender}: ${text}`);
  });

  return transcriptLines.join("\n");
}

function attachFullChatScanner() {
  const chatHeader = document.querySelector("#main header, header[role='banner'], div[role='region'] header");
  if (!chatHeader || chatHeader.dataset.sentinelleFullHeader) return;
  chatHeader.dataset.sentinelleFullHeader = "true";

  const transcript = extractFullChatTranscript();
  if (!transcript || transcript.length < 10) return;

  const lowerTrans = transcript.toLowerCase();
  const SELLER_KEYWORDS = ["prix", "vente", "vendre", "article", "acompte", "livraison", "orange money", "mtn", "wave", "moov", "avance", "payer", "combien", "compte", "iphone"];
  const HAS_SELLER_TERMS = SELLER_KEYWORDS.some((kw) => lowerTrans.includes(kw));
  const HAS_URL = lowerTrans.includes("http://") || lowerTrans.includes("https://") || lowerTrans.includes(".com") || lowerTrans.includes(".ci") || lowerTrans.includes(".xyz");

  if (HAS_SELLER_TERMS || HAS_URL) {
    const banner = document.createElement("div");
    banner.className = "sentinelle-fullchat-bar";
    banner.innerHTML = `
      <span>${ICONS.store} <strong>Transaction Vendeur / Lien Détecté</strong></span>
      <button class="sentinelle-scan-full-btn">${ICONS.shield} Analyser Toute la Conversation</button>
    `;

    banner.querySelector(".sentinelle-scan-full-btn").onclick = (e) => {
      e.stopPropagation();
      const currentTranscript = extractFullChatTranscript();
      const btn = e.target;
      btn.innerHTML = `⏳ Analyse IA de l'échange...`;

      extApi.runtime.sendMessage(
        { type: "ANALYZE_CONVERSATION", transcript: currentTranscript },
        (response) => {
          btn.innerHTML = `${ICONS.shield} Analyser Toute la Conversation`;
          if (response && response.success) {
            showFullChatModal(response.data);
          } else {
            alert("Erreur lors de l'analyse de la conversation.");
          }
        }
      );
    };

    chatHeader.appendChild(banner);
  }
}

// Écouter les changements dans la page (DOM Observer)
const observer = new MutationObserver(() => {
  attachScanButtons();
  attachFullChatScanner();
});

observer.observe(document.body, { childList: true, subtree: true });
attachScanButtons();
attachFullChatScanner();
