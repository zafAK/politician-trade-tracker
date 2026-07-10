import { useRef, useState } from "react";
import { api } from "../api/client";
import type { ChatResponse, ToolCallTrace } from "../api/types";

interface Message {
  role: "user" | "assistant";
  content: string;
  tools?: ToolCallTrace[];
}

const SUGGESTIONS = [
  "Who traded NVDA the most?",
  "What has Nancy Pelosi been trading?",
  "What are the most traded stocks?",
  "Show me recent trades",
];

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const send = async (text: string) => {
    const question = text.trim();
    if (!question || busy) return;
    setInput("");
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { role: "user", content: question }]);
    setBusy(true);
    try {
      const res: ChatResponse = await api.chat(question, history);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, tools: res.tool_calls },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: ${String(e)}` },
      ]);
    } finally {
      setBusy(false);
      requestAnimationFrame(() =>
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight }),
      );
    }
  };

  return (
    <div className="card chat">
      <div className="chat-head">
        <h2>Ask the agent</h2>
        <span className="chat-sub">Tool-calling over the live database</span>
      </div>

      <div className="chat-log" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>Ask a question about congressional trades:</p>
            <div className="suggestions">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="chip" onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`bubble-row ${m.role}`}>
            <div className={`bubble ${m.role}`}>
              {m.content}
              {m.tools && m.tools.length > 0 && <ToolTrace tools={m.tools} />}
            </div>
          </div>
        ))}

        {busy && <div className="bubble-row assistant"><div className="bubble assistant typing">…</div></div>}
      </div>

      <form
        className="chat-input"
        onSubmit={(e) => {
          e.preventDefault();
          void send(input);
        }}
      >
        <input
          className="input"
          placeholder="Ask about a ticker or a member…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={busy}
        />
        <button className="btn" type="submit" disabled={busy || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

function ToolTrace({ tools }: { tools: ToolCallTrace[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="tool-trace">
      <button className="trace-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "▾" : "▸"} {tools.length} tool call{tools.length > 1 ? "s" : ""} used
      </button>
      {open && (
        <div className="trace-body">
          {tools.map((t, i) => (
            <div key={i} className="trace-item">
              <code className="trace-name">
                {t.name}({Object.entries(t.arguments)
                  .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
                  .join(", ")})
              </code>
              <div className="trace-result">{t.result_preview}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
