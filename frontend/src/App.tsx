import { Dashboard } from "./pages/Dashboard";
import "./App.css";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Capitol Trades</h1>
          <p className="tagline">
            Congressional stock disclosures — browse the data, then ask the
            agent.
          </p>
        </div>
      </header>
      <main>
        <Dashboard />
      </main>
      <footer className="app-footer">
        Data: public STOCK Act disclosures · For demonstration purposes
      </footer>
    </div>
  );
}
