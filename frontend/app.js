const API_BASE = "";

// Tabs
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById("tab-" + tab.dataset.tab).classList.add("active");
  });
});

document.getElementById("image-input").addEventListener("change", (e) => {
  const file = e.target.files[0];
  document.getElementById("image-filename").textContent = file
    ? "📷 " + file.name
    : "📷 Importer une capture d'ecran";
});

let lastMessageForReply = "";
let lastScamType = "";
let currentOfficialReport = "";
let currentExplanation = "";

function showLoading(show) {
  document.getElementById("loading").classList.toggle("hidden", !show);
  document.getElementById("result").classList.toggle("hidden", show);
}

function updateGauge(score) {
  const fillCircle = document.getElementById("gauge-fill");
  const circumference = 314.15;
  const offset = circumference - (score / 100) * circumference;
  fillCircle.style.strokeDashoffset = offset;

  let strokeColor = "#52c41a"; // Ok green
  if (score >= 30 && score < 60) strokeColor = "#ffa940"; // Warning orange
  else if (score >= 60 && score < 80) strokeColor = "#ff7a45"; // High orange
  else if (score >= 80) strokeColor = "#ff4d4f"; // Danger red

  fillCircle.style.stroke = strokeColor;
}

function renderResult(data) {
  document.getElementById("result").classList.remove("hidden");
  document.getElementById("result-emoji").textContent = data.level_emoji || "🟢";
  document.getElementById("result-level").textContent = "RISQUE " + (data.level || "FAIBLE");
  document.getElementById("result-score").textContent = data.score;
  document.getElementById("result-type").textContent = data.scam_type || "—";
  document.getElementById("result-explanation").textContent = data.explanation || "—";

  currentExplanation = data.explanation || "Aucun signal détecté.";
  currentOfficialReport = data.official_report || "";

  updateGauge(data.score || 0);

  // Render psychological triggers
  const triggersContainer = document.getElementById("result-triggers");
  triggersContainer.innerHTML = "";
  const triggers = data.psychological_triggers || [];
  if (triggers.length > 0) {
    document.getElementById("triggers-block").style.display = "block";
    triggers.forEach((t) => {
      const chip = document.createElement("div");
      chip.className = "trigger-chip";
      chip.title = t.description;
      chip.textContent = t.name;
      triggersContainer.appendChild(chip);
    });
  } else {
    document.getElementById("triggers-block").style.display = "none";
  }

  // Render signals
  const signalsList = document.getElementById("result-signals");
  signalsList.innerHTML = "";
  (data.signals || []).forEach((s) => {
    const li = document.createElement("li");
    li.textContent = s;
    signalsList.appendChild(li);
  });
  if ((data.signals || []).length === 0) {
    const li = document.createElement("li");
    li.textContent = "Aucun signal détecté";
    signalsList.appendChild(li);
  }

  // Render recommendations
  const recList = document.getElementById("result-recommendations");
  recList.innerHTML = "";
  (data.recommendations || []).forEach((r) => {
    const li = document.createElement("li");
    li.textContent = r;
    recList.appendChild(li);
  });

  // Verification & typosquatting block
  const verifBlock = document.getElementById("verification-block");
  let verifText = data.verification_note || "";
  if (data.typosquatting_detected) {
    verifText = (verifText ? verifText + " — " : "") + "⚠️ ALERTE : Typosquatting/Imitation de marque détecté !";
  }
  if (verifText) {
    verifBlock.style.display = "block";
    document.getElementById("result-verification").textContent = verifText;
  } else {
    verifBlock.style.display = "none";
  }

  document.getElementById("reply-block").classList.add("hidden");
  document.getElementById("report-block").classList.add("hidden");
  lastScamType = data.scam_type || "";
}

// Natural French Voice selector for Web Speech API
function getNaturalFrenchVoice() {
  const voices = window.speechSynthesis.getVoices();
  const frVoices = voices.filter((v) => v.lang && v.lang.toLowerCase().startsWith("fr"));
  if (frVoices.length === 0) return null;

  const naturalVoice = frVoices.find(
    (v) =>
      v.name.includes("Google") ||
      v.name.includes("Natural") ||
      v.name.includes("Neural") ||
      v.name.includes("Premium") ||
      v.name.includes("Thomas") ||
      v.name.includes("Hortense") ||
      v.name.includes("Julie") ||
      v.name.includes("Paul")
  );

  return naturalVoice || frVoices[0];
}

if ("speechSynthesis" in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
  };
}

// Audio alert (TTS)
document.getElementById("btn-audio-alert").addEventListener("click", () => {
  if (!("speechSynthesis" in window)) {
    return alert("Synthèse vocale non supportée sur ce navigateur.");
  }
  window.speechSynthesis.cancel();

  const levelText = document.getElementById("result-level").textContent;
  const cleanExplanation = currentExplanation
    .replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]/gu, "")
    .replace(/\s+/g, " ")
    .trim();

  const textToRead = `Alerte de sécurité 0xSentinelle. Niveau de risque : ${levelText}. ${cleanExplanation}`;

  const utterance = new SpeechSynthesisUtterance(textToRead);
  utterance.lang = "fr-FR";
  utterance.rate = 0.93; // Rhythm plus calme et naturel
  utterance.pitch = 1.0;

  const bestVoice = getNaturalFrenchVoice();
  if (bestVoice) {
    utterance.voice = bestVoice;
  }

  window.speechSynthesis.speak(utterance);
});


// Official Report
document.getElementById("btn-show-report").addEventListener("click", () => {
  const reportBlock = document.getElementById("report-block");
  reportBlock.classList.toggle("hidden");
  if (!reportBlock.classList.contains("hidden")) {
    document.getElementById("report-text").value = currentOfficialReport || "Aucun rapport généré.";
  }
});

document.getElementById("btn-copy-report").addEventListener("click", () => {
  const reportText = document.getElementById("report-text").value;
  navigator.clipboard.writeText(reportText).then(() => {
    alert("Rapport officiel copié dans le presse-papier !");
  }).catch(() => {
    alert("Erreur lors de la copie.");
  });
});

async function postJSON(url, body) {
  const res = await fetch(API_BASE + url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("Erreur serveur (" + res.status + ")");
  return res.json();
}

document.getElementById("btn-analyze-text").addEventListener("click", async () => {
  const message = document.getElementById("message-input").value.trim();
  const brand = document.getElementById("brand-text").value.trim();
  if (!message) return alert("Veuillez saisir un message.");
  lastMessageForReply = message;
  showLoading(true);
  try {
    const data = await postJSON("/analyze/text", { message, claimed_brand: brand || null });
    renderResult(data);
  } catch (e) {
    alert("Erreur lors de l'analyse : " + e.message);
  } finally {
    showLoading(false);
  }
});

document.getElementById("btn-analyze-url").addEventListener("click", async () => {
  const url = document.getElementById("url-input").value.trim();
  const brand = document.getElementById("brand-url").value.trim();
  if (!url) return alert("Veuillez saisir une URL.");
  lastMessageForReply = url;
  showLoading(true);
  try {
    const data = await postJSON("/analyze/url", { url, claimed_brand: brand || null });
    renderResult(data);
  } catch (e) {
    alert("Erreur lors de l'analyse : " + e.message);
  } finally {
    showLoading(false);
  }
});

document.getElementById("btn-analyze-image").addEventListener("click", async () => {
  const fileInput = document.getElementById("image-input");
  const brand = document.getElementById("brand-image").value.trim();
  if (!fileInput.files[0]) return alert("Veuillez importer une capture.");
  showLoading(true);
  try {
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    if (brand) formData.append("claimed_brand", brand);
    const res = await fetch(API_BASE + "/analyze/image", { method: "POST", body: formData });
    if (!res.ok) throw new Error("Erreur serveur (" + res.status + ")");
    const data = await res.json();
    lastMessageForReply = "(contenu de la capture d'ecran analysee)";
    renderResult(data);
  } catch (e) {
    alert("Erreur lors de l'analyse : " + e.message);
  } finally {
    showLoading(false);
  }
});

document.getElementById("btn-generate-reply").addEventListener("click", async () => {
  const btn = document.getElementById("btn-generate-reply");
  btn.disabled = true;
  btn.textContent = "Génération...";
  try {
    const data = await postJSON("/analyze/reply", {
      original_message: lastMessageForReply || "message suspect",
      scam_type: lastScamType,
    });
    document.getElementById("reply-block").classList.remove("hidden");
    document.getElementById("reply-text").textContent = data.reply;
  } catch (e) {
    alert("Erreur lors de la génération : " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "💬 Générer une réponse";
  }
});

