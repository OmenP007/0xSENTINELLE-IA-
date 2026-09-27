import { motion } from "framer-motion";

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

      <p className="tagline">Scan before you trust. 🇨🇮 — Anti-arnaque · Côte d'Ivoire</p>

      <div className="badge-multiagent">
        <span className="badge-dot" />
        Agents actifs : Texte · Capture · URL · Voix IA
      </div>
    </motion.header>
  );
}
