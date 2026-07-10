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
        Data: public STOCK Act disclosures ·{" "}
        <a
          href="https://raw.githubusercontent.com/timothycarambat/senate-stock-watcher-data/master/aggregate/all_transactions.json"
          target="_blank"
          rel="noopener noreferrer"
        >
          senate-stock-watcher-data
        </a>
      </footer>
    </div>
  );
}
