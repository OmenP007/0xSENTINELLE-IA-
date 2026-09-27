import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Camera, Link, Zap, Search, CheckCircle2 } from "lucide-react";
import { postJSON, postFormData } from "../api";
import ResultCard from "./ResultCard";

const TAB_ICONS = { text: <Mail size={16} />, image: <Camera size={16} />, url: <Link size={16} /> };
const TAB_LABELS = { text: "Message", image: "Capture", url: "URL" };

const CI_BRANDS_PLACEHOLDER = "ex: Orange Money, MTN Mobile, Wave CI, Moov Money";

// ─── Loading Overlay ──────────────────────────────────────────────────────────
function LoadingOverlay() {
  return (
    <motion.div
      className="loading-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="loading-ring" />
      <div className="loading-dots">
        <div className="loading-dot" />
        <div className="loading-dot" />
        <div className="loading-dot" />
      </div>
      <p className="loading-text">Analyse Multi-Agents en cours...</p>
    </motion.div>
  );
}

// ─── Text Tab ─────────────────────────────────────────────────────────────────
function TextTab({ onResult }) {
  const [message, setMessage] = useState("");
  const [brand, setBrand] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!message.trim()) return;
    setLoading(true);
    try {
      const data = await postJSON("/analyze/text", {
        message: message.trim(),
        claimed_brand: brand.trim() || null,
      });
      onResult(data, message.trim());
    } catch (e) {
      alert("Erreur : " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="input-group">
      <textarea
        className="textarea-scan"
        placeholder="Collez ici votre SMS, message WhatsApp, email ou texte suspect... (Nouchi, Dioula ou Français)"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <input
        className="input-field"
        type="text"
        placeholder={`Marque revendiquée (${CI_BRANDS_PLACEHOLDER})`}
        value={brand}
        onChange={(e) => setBrand(e.target.value)}
      />
      <button className="analyze-btn" onClick={handleAnalyze} disabled={loading || !message.trim()}>
        <Zap size={16} style={{ marginRight: 6 }} />
        {loading ? "Analyse en cours..." : "Analyser avec l'Agent IA"}
      </button>
      {loading && <LoadingOverlay />}
    </div>
  );
}

// ─── Image Tab ────────────────────────────────────────────────────────────────
function ImageTab({ onResult }) {
  const [file, setFile] = useState(null);
  const [brand, setBrand] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      if (brand.trim()) fd.append("claimed_brand", brand.trim());
      const data = await postFormData("/analyze/image", fd);
      onResult(data, "(capture d'écran analysée)");
    } catch (e) {
      alert("Erreur : " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="input-group">
      <label
        className={`upload-zone ${file ? "has-file" : ""}`}
        onClick={() => fileInputRef.current?.click()}
      >
        <span className="upload-zone-icon">
          {file ? <CheckCircle2 size={32} color="#22c55e" /> : <Camera size={32} color="#60a5fa" />}
        </span>
        <span className="upload-zone-label">
          {file ? file.name : "Importer une capture d'écran"}
        </span>
        <span className="upload-zone-sub">
          {file ? "Cliquer pour changer" : "PNG, JPG, JPEG — Drag & drop ou cliquer"}
        </span>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          hidden
          onChange={(e) => setFile(e.target.files[0] || null)}
        />
      </label>
      <input
        className="input-field"
        type="text"
        placeholder={`Marque revendiquée (${CI_BRANDS_PLACEHOLDER})`}
        value={brand}
        onChange={(e) => setBrand(e.target.value)}
      />
      <button className="analyze-btn" onClick={handleAnalyze} disabled={loading || !file}>
        <Search size={16} style={{ marginRight: 6 }} />
        {loading ? "Analyse en cours..." : "Analyser la capture"}
      </button>
      {loading && <LoadingOverlay />}
    </div>
  );
}

// ─── URL Tab ──────────────────────────────────────────────────────────────────
function UrlTab({ onResult }) {
  const [url, setUrl] = useState("");
  const [brand, setBrand] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!url.trim()) return;
    setLoading(true);
    try {
      const data = await postJSON("/analyze/url", {
        url: url.trim(),
        claimed_brand: brand.trim() || null,
      });
      onResult(data, url.trim());
    } catch (e) {
      alert("Erreur : " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="input-group">
      <input
        className="input-field"
        type="text"
        placeholder="https://site-suspect.com (orange-money-ci.com, mtn-promo-ci.net...)"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
      />
      <input
        className="input-field"
        type="text"
        placeholder={`Marque revendiquée (${CI_BRANDS_PLACEHOLDER})`}
        value={brand}
        onChange={(e) => setBrand(e.target.value)}
      />
      <button className="analyze-btn" onClick={handleAnalyze} disabled={loading || !url.trim()}>
        <Link size={16} style={{ marginRight: 6 }} />
        {loading ? "Analyse en cours..." : "Analyser l'URL"}
      </button>
      {loading && <LoadingOverlay />}
    </div>
  );
}

// ─── Main ScanPanel ───────────────────────────────────────────────────────────
export default function ScanPanel() {
  const [activeTab, setActiveTab] = useState("text");
  const [result, setResult] = useState(null);
  const [lastMessage, setLastMessage] = useState("");

  const handleResult = (data, message) => {
    setResult(data);
    setLastMessage(message);
  };

  const tabs = ["text", "image", "url"];

  return (
    <div className="main-panel">
      {/* Tabs */}
      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? "active" : ""}`}
            onClick={() => { setActiveTab(tab); setResult(null); }}
          >
            <span>{TAB_ICONS[tab]}</span>
            <span>{TAB_LABELS[tab]}</span>
          </button>
        ))}
      </div>


      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === "text" && <TextTab onResult={handleResult} />}
          {activeTab === "image" && <ImageTab onResult={handleResult} />}
          {activeTab === "url" && <UrlTab onResult={handleResult} />}
        </motion.div>
      </AnimatePresence>

      {/* Result */}
      <AnimatePresence>
        {result && (
          <ResultCard
            key={JSON.stringify(result)}
            data={result}
            originalMessage={lastMessage}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
