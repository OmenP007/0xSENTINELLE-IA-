// API configuration
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function postJSON(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Erreur serveur (${res.status})`);
  return res.json();
}

export async function postFormData(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`Erreur serveur (${res.status})`);
  return res.json();
}

export async function fetchVoiceMP3(score, level, explanation, scamType) {
  const res = await fetch(`${API_BASE}/voice/alert`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      score,
      level,
      explanation,
      scam_type: scamType || "",
      lang: "fr",
    }),
  });
  if (!res.ok) throw new Error("Voix indisponible");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}
