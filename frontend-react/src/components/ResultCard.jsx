import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { fetchVoiceMP3, postJSON } from "../api";

// ─── Score Gauge SVG ───────────────────────────────────────────────────────────
function ScoreGauge({ score, level, emoji }) {
  const circumference = 314.15;
  const offset = circumference - (score / 100) * circumference;

  const strokeColor =
    score >= 80 ? "#ff4d4f"
    : score >= 60 ? "#ffa940"
    : score >= 30 ? "#ffd93d"
    : "#52c41a";

  const levelColor =
    score >= 80 ? "#ff4d4f"
    : score >= 60 ? "#ffa940"
    : score >= 30 ? "#ffd93d"
    : "#52c41a";

  return (
    <div className="gauge-wrapper">
      <svg className="gauge-svg" viewBox="0 0 120 120" style={{ color: strokeColor }}>
        <circle className="gauge-bg" cx="60" cy="60" r="50" />
        <circle
          className="gauge-fill"
          cx="60" cy="60" r="50"
          style={{ stroke: strokeColor, strokeDashoffset: offset }}
        />
      </svg>
      <div className="score-center">
        <div className="score-emoji">{emoji}</div>
        <motion.div
          className="score-value"
          style={{ color: levelColor }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
        >
          {score}
        </motion.div>
        <div className="score-max">/ 100</div>
      </div>
    </div>
  );
}

// ─── Voice Button ─────────────────────────────────────────────────────────────
function VoiceButton({ score, level, explanation, scamType }) {
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const audioRef = useRef(null);

  const handleClick = async () => {
    if (playing) {
      audioRef.current?.pause();
      setPlaying(false);
      return;
    }

    setLoading(true);
    try {
      // Essai 1 : backend gTTS
      const url = await fetchVoiceMP3(score, level, explanation, scamType);
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = () => setPlaying(false);
      audio.onerror = () => {
        // Fallback Web Speech API
        useFallbackTTS(level, explanation);
        setPlaying(false);
      };
      audio.play();
      setPlaying(true);
    } catch {
      // Fallback Web Speech API
      useFallbackTTS(level, explanation);
    } finally {
      setLoading(false);
    }
  };

  const useFallbackTTS = (level, explanation) => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const text = `Alerte 0xSentinelle. Niveau ${level}. ${explanation
      .replace(/[\u{1F300}-\u{1F9FF}]/gu, "")
      .trim()}`;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "fr-FR";
    utterance.rate = 0.92;
    utterance.pitch = 1.0;
    const voices = window.speechSynthesis.getVoices();
    const frVoice = voices.find(
      (v) =>
        v.lang?.startsWith("fr") &&
        (v.name.includes("Google") || v.name.includes("Thomas") || v.name.includes("Neural"))
    );
    if (frVoice) utterance.voice = frVoice;
    utterance.onend = () => setPlaying(false);
    window.speechSynthesis.speak(utterance);
    setPlaying(true);
  };

  return (
    <button
      className={`voice-btn ${playing ? "playing" : ""}`}
      onClick={handleClick}
      disabled={loading}
      title={playing ? "Arrêter la lecture" : "Écouter l'alerte vocale"}
    >
      {loading ? "⏳" : playing ? "⏹" : "🔊"}
      {loading ? "Génération..." : playing ? "Arrêter" : "Écouter l'alerte vocale"}
    </button>
  );
}

// ─── Confidence Badge ─────────────────────────────────────────────────────────
function ConfidenceBadge({ confidence }) {
  const map = { high: "Haute confiance", medium: "Confiance moyenne", low: "Faible confiance" };
  return (
    <span className={`confidence-badge confidence-${confidence}`}>
      {confidence === "high" ? "●" : confidence === "medium" ? "◐" : "○"}{" "}
      {map[confidence] || confidence}
    </span>
  );
}

// ─── Language Badge ───────────────────────────────────────────────────────────
function LangBadge({ lang }) {
  const map = {
    fr: "🇫🇷 Français",
    nouchi: "🇨🇮 Nouchi",
    dioula: "🇨🇮 Dioula",
    en: "🇬🇧 English",
    mixte: "🌍 Mixte",
  };
  return <span className="lang-badge">{map[lang] || lang}</span>;
}

// ─── Main ResultCard ──────────────────────────────────────────────────────────
export default function ResultCard({ data, originalMessage, onReply }) {
  const [replyText, setReplyText] = useState("");
  const [loadingReply, setLoadingReply] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [showReply, setShowReply] = useState(false);
  const [copied, setCopied] = useState(false);

  const { score, level, level_emoji, scam_type, explanation, signals, psychological_triggers,
    recommendations, confidence, language_detected, verification_note, typosquatting_detected,
    official_report } = data;

  const handleGenerateReply = async () => {
    setLoadingReply(true);
    try {
      const res = await postJSON("/analyze/reply", {
        original_message: originalMessage || "message suspect",
        scam_type: scam_type,
      });
      setReplyText(res.reply);
      setShowReply(true);
    } catch {
      setReplyText("Bonjour, je préfère vérifier cette demande directement auprès du service officiel avant d'agir. Merci.");
      setShowReply(true);
    } finally {
      setLoadingReply(false);
    }
  };

  const handleCopyReport = () => {
    navigator.clipboard.writeText(official_report || "Aucun rapport").then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
  };

  return (
    <motion.div className="result-section" variants={cardVariants} initial="hidden" animate="visible">
      {/* Score Card */}
      <div className="score-card">
        <ScoreGauge score={score || 0} level={level} emoji={level_emoji || "🟢"} />
        <div className="score-level" style={{
          color: score >= 80 ? "#ff4d4f" : score >= 60 ? "#ffa940" : score >= 30 ? "#ffd93d" : "#52c41a"
        }}>
          RISQUE {level}
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap", justifyContent: "center" }}>
          {confidence && <ConfidenceBadge confidence={confidence} />}
          {language_detected && <LangBadge lang={language_detected} />}
        </div>

        <VoiceButton
          score={score || 0}
          level={level}
          explanation={explanation}
          scamType={scam_type}
        />
      </div>

      {/* Triggers psychologiques */}
      <AnimatePresence>
        {psychological_triggers?.length > 0 && (
          <motion.div className="detail-block"
            initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}>
            <div className="detail-title">🧠 Déclencheurs Psychologiques</div>
            <div className="triggers-grid">
              {psychological_triggers.map((t, i) => (
                <div key={i} className="trigger-chip" title={t.description}>
                  ⚡ {t.name}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Type probable */}
      <div className="detail-block">
        <div className="detail-title">🎯 Type Détecté</div>
        <p className="detail-text">{scam_type?.replace(/_/g, " ") || "—"}</p>
      </div>

      {/* Typosquatting / Vérification */}
      {(verification_note || typosquatting_detected) && (
        <div className="detail-block">
          <div className="detail-title">🔍 Vérification Officielle</div>
          {typosquatting_detected && (
            <div className="typosquatting-alert">
              ⚠️ ALERTE : Typosquatting / Imitation de marque détectée !
            </div>
          )}
          {verification_note && (
            <div className="verification-alert" style={{ marginTop: typosquatting_detected ? 8 : 0 }}>
              ℹ️ {verification_note}
            </div>
          )}
        </div>
      )}

      {/* Signaux détectés */}
      <div className="detail-block">
        <div className="detail-title">⚠️ Signaux Détectés</div>
        {signals?.length > 0 ? (
          <ul className="signals-list">
            {signals.map((s, i) => (
              <li key={i} className="signal-item">
                <span className="signal-dot" />
                {s.replace(/_/g, " ")}
              </li>
            ))}
          </ul>
        ) : (
          <p className="detail-text" style={{ color: "var(--text-muted)" }}>Aucun signal détecté</p>
        )}
      </div>

      {/* Explication */}
      <div className="detail-block">
        <div className="detail-title">🤖 Synthèse de l'Agent IA</div>
        <p className="detail-text">{explanation || "—"}</p>
      </div>

      {/* Recommandations */}
      {recommendations?.length > 0 && (
        <div className="detail-block">
          <div className="detail-title">🛡️ Recommandations</div>
          <ul className="reco-list">
            {recommendations.map((r, i) => (
              <li key={i} className="reco-item">
                <span className="reco-icon">✓</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="actions-row">
        <button className="action-btn" onClick={handleGenerateReply} disabled={loadingReply}>
          {loadingReply ? "⏳" : "💬"} {loadingReply ? "Génération..." : "Générer réponse"}
        </button>
        {official_report && (
          <button className="action-btn" onClick={() => setShowReport(!showReport)}>
            📋 {showReport ? "Masquer" : "Signalement Officiel"}
          </button>
        )}
      </div>

      {/* Reply Block */}
      <AnimatePresence>
        {showReply && replyText && (
          <motion.div className="collapsible-block"
            initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}>
            <div className="detail-title">💬 Réponse Prudente Suggérée</div>
            <p className="detail-text">{replyText}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Report Block */}
      <AnimatePresence>
        {showReport && official_report && (
          <motion.div className="collapsible-block"
            initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}>
            <div className="detail-title">📋 Rapport d'Abus Officiel</div>
            <textarea className="report-textarea" readOnly rows={8} value={official_report} />
            <button className="analyze-btn" style={{ marginTop: 10 }} onClick={handleCopyReport}>
              {copied ? "✅ Copié !" : "📋 Copier le rapport"}
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
