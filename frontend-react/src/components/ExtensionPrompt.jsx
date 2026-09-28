import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function ExtensionPrompt() {
  const [showBanner, setShowBanner] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // Vérifie si l'utilisateur a déjà masqué la bannière
    const dismissed = localStorage.getItem("0xsentinelle_ext_dismissed");
    if (!dismissed) {
      // Petite temporisation pour un effet d'entrée fluide
      const timer = setTimeout(() => setShowBanner(true), 1200);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleDismiss = () => {
    setShowBanner(false);
    localStorage.setItem("0xsentinelle_ext_dismissed", "true");
  };

  return (
    <>
      {/* BANNIÈRE FLOTTANTE SUR LE SITE */}
      <AnimatePresence>
        {showBanner && (
          <motion.div
            className="extension-banner"
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
          >
            <button className="btn-ext-close" onClick={handleDismiss} title="Fermer la bannière">
              ✕
            </button>
            <div className="ext-banner-content">
              <div className="ext-banner-icon">🧩</div>
              <div className="ext-banner-text">
                <strong>Protections Chrome & Brave en temps réel !</strong>
                <span>Scannez vos emails, SMS WhatsApp et pages web contre les arnaques.</span>
              </div>
            </div>

            <div className="ext-banner-actions">
              <a
                href="/0xsentinelle-extension.zip"
                download="0xsentinelle-extension.zip"
                className="btn-ext-download"
                onClick={() => setShowModal(true)}
              >
                📥 Télécharger l'Extension
              </a>
              <button className="btn-ext-guide" onClick={() => setShowModal(true)}>
                📖 Guide (30s)
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* MODAL DU GUIDE D'INSTALLATION */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            className="ext-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowModal(false)}
          >
            <motion.div
              className="ext-modal-content"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="ext-modal-header">
                <h3>🧩 Installation de l'Extension Chrome 0xSentinelle</h3>
                <button className="ext-modal-close" onClick={() => setShowModal(false)}>
                  ✕
                </button>
              </div>

              <div className="ext-modal-body">
                <p className="ext-intro">
                  Protégez votre navigateur en temps réel. L'extension analyse automatiquement les liens suspects et les tentatives de phishing sur WhatsApp, Facebook et vos emails.
                </p>

                <div className="ext-steps">
                  <div className="ext-step">
                    <span className="step-num">1</span>
                    <div className="step-desc">
                      <strong>Télécharger et Dézipper</strong>
                      <p>
                        <a href="/0xsentinelle-extension.zip" download="0xsentinelle-extension.zip" className="step-dl-link">
                          Cliquez ici pour télécharger 0xSentinelle-Extension (.zip)
                        </a>{" "}
                        puis extrayez le fichier ZIP sur votre ordinateur.
                      </p>
                    </div>
                  </div>

                  <div className="ext-step">
                    <span className="step-num">2</span>
                    <div className="step-desc">
                      <strong>Ouvrir les Extensions Chrome</strong>
                      <p>
                        Tapez <code>chrome://extensions</code> dans la barre d'adresse de votre navigateur (Chrome, Brave, Edge).
                      </p>
                    </div>
                  </div>

                  <div className="ext-step">
                    <span className="step-num">3</span>
                    <div className="step-desc">
                      <strong>Activer le "Mode Développeur"</strong>
                      <p>Basculez le bouton **Mode Développeur** situé en haut à droite de la page des extensions.</p>
                    </div>
                  </div>

                  <div className="ext-step">
                    <span className="step-num">4</span>
                    <div className="step-desc">
                      <strong>Charger l'Extension</strong>
                      <p>Cliquez sur **"Charger l'extension non empaquetée"** (Load unpacked) et sélectionnez le dossier dézippé.</p>
                    </div>
                  </div>
                </div>

                <div className="ext-footer-note">
                  🛡️ <em>0xSentinelle IA surveillera désormais votre navigation en temps réel.</em>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
