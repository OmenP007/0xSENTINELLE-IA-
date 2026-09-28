import { motion } from "framer-motion";
import { Send, Puzzle } from "lucide-react";

export default function Header() {
  return (
    <motion.header
      className="hero"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <div className="logo">
        <span className="logo-hex">0x</span>
        <span className="logo-name">Sentinelle</span>
        <span className="logo-ia"> IA</span>
      </div>

      <p className="tagline">Scan before you trust. — Anti-arnaque · Côte d'Ivoire</p>

      <div className="header-nav-badges">
        <div className="badge-multiagent">
          <span className="badge-dot" />
          Agents actifs : Texte · Capture · URL · Voix IA
        </div>
        <a
          href="https://t.me/deadbeef225bot"
          target="_blank"
          rel="noopener noreferrer"
          className="badge-telegram-btn"
          title="Ouvrir le Bot Telegram @deadbeef225bot"
        >
          <Send size={14} style={{ marginRight: 4 }} /> Bot Telegram @deadbeef225bot
        </a>
        <a
          href="/0xsentinelle-extension.zip"
          download="0xsentinelle-extension.zip"
          className="badge-extension-btn"
          title="Installer l'extension Chrome / Brave"
        >
          <Puzzle size={14} style={{ marginRight: 4 }} /> Extension Browser
        </a>
      </div>
    </motion.header>
  );
}
