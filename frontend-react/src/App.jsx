import './index.css'
import Header from './components/Header'
import ScanPanel from './components/ScanPanel'
import ExtensionPrompt from './components/ExtensionPrompt'

function App() {
  return (
    <div className="app-container">
      <ExtensionPrompt />
      <div className="app-inner">
        <Header />
        <ScanPanel />
        <footer className="footer">
          <p>
            <span>0xSentinelle IA</span> — Protection Anti-Arnaques 🇨🇮 Côte d'Ivoire ·
            Signalement : ARTCI · PJ Cybercriminalité <span>+225 27 20 25 98 72</span>
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
