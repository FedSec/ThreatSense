"use client";

import { useEffect, useRef, useState } from "react";
import Navigation from "@/components/Navigation";
import { colors, styles } from "@/styles/theme";
import { API_BASE } from "@/lib/api";

type Tab = "chat" | "code";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const LANGUAGES = [
  "auto-detect", "Python", "JavaScript", "TypeScript", "PHP", "Java",
  "C", "C++", "C#", "Go", "Ruby", "Rust", "SQL", "Bash/Shell",
  "Kotlin", "Swift", "Scala", "HTML", "YAML", "Dockerfile",
];

async function streamRequest(
  path: string,
  body: object,
  token: string,
  onChunk: (text: string) => void,
  onError: (err: string) => void,
  onDone: () => void,
) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok || !res.body) {
      onError(`Request failed (${res.status})`);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const data = line.slice(6).trim();
        if (data === "[DONE]") { onDone(); return; }
        try {
          const parsed = JSON.parse(data);
          if (parsed.text) onChunk(parsed.text);
          if (parsed.error) onError(parsed.error);
        } catch { /* skip malformed lines */ }
      }
    }
    onDone();
  } catch (e: any) {
    onError(e?.message ?? "Network error");
  }
}

export default function AIPage() {
  const [token, setToken] = useState("");
  const [tab, setTab] = useState<Tab>("chat");

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [includeFindings, setIncludeFindings] = useState(true);
  const [chatStreaming, setChatStreaming] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Code analysis state
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("auto-detect");
  const [filename, setFilename] = useState("");
  const [codeOutput, setCodeOutput] = useState("");
  const [codeStreaming, setCodeStreaming] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem("ts_token") || "";
    if (!t) { window.location.href = "/login"; return; }
    setToken(t);
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || chatStreaming) return;
    const userMsg = input.trim();
    setInput("");

    const history = messages.map(m => ({ role: m.role, content: m.content }));
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setMessages(prev => [...prev, { role: "assistant", content: "" }]);
    setChatStreaming(true);

    streamRequest(
      "/ai/chat",
      { message: userMsg, history, include_findings: includeFindings },
      token,
      (text) => setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content: updated[updated.length - 1].content + text,
        };
        return updated;
      }),
      (err) => {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "assistant", content: `Error: ${err}` };
          return updated;
        });
        setChatStreaming(false);
      },
      () => setChatStreaming(false),
    );
  }

  async function analyzeCode() {
    if (!code.trim() || codeStreaming) return;
    setCodeOutput("");
    setCodeStreaming(true);

    streamRequest(
      "/ai/analyze-code",
      { code, language, filename: filename || undefined },
      token,
      (text) => setCodeOutput(prev => prev + text),
      (err) => { setCodeOutput(`Error: ${err}`); setCodeStreaming(false); },
      () => setCodeStreaming(false),
    );
  }

  const tabStyle = (t: Tab): React.CSSProperties => ({
    padding: "10px 24px",
    borderRadius: "8px 8px 0 0",
    border: `1px solid ${tab === t ? colors.borderPrimary : colors.borderSecondary}`,
    borderBottom: tab === t ? "none" : `1px solid ${colors.borderSecondary}`,
    background: tab === t ? colors.bgCard : "transparent",
    color: tab === t ? colors.primary : colors.textSecondary,
    fontSize: "14px",
    fontWeight: 600,
    cursor: "pointer",
    outline: "none",
    marginBottom: "-1px",
    position: "relative",
  });

  return (
    <main style={{ ...styles.container, minHeight: "100vh" }}>
      <Navigation />

      <h1 style={{ fontSize: "40px", margin: 0, marginBottom: "8px", color: colors.textPrimary, fontWeight: 700 }}>
        AI Security Advisor
      </h1>
      <p style={{ marginTop: 0, marginBottom: "32px", color: colors.textSecondary, fontSize: "16px" }}>
        Ask anything about your findings, get educated on vulnerabilities, or scan source code
      </p>

      {/* Tabs */}
      <div style={{ display: "flex", gap: "4px", marginBottom: 0 }}>
        <button style={tabStyle("chat")} onClick={() => setTab("chat")}>AI Chat</button>
        <button style={tabStyle("code")} onClick={() => setTab("code")}>Code Scanner</button>
      </div>

      <div style={{
        border: `1px solid ${colors.borderPrimary}`,
        borderRadius: "0 12px 12px 12px",
        background: colors.bgCard,
        padding: "24px",
        boxShadow: `0 0 20px rgba(0,102,255,0.15)`,
      }}>

        {/* ── CHAT TAB ── */}
        {tab === "chat" && (
          <div style={{ display: "flex", flexDirection: "column", height: "600px" }}>
            {/* Messages */}
            <div style={{
              flex: 1,
              overflowY: "auto",
              marginBottom: "16px",
              display: "flex",
              flexDirection: "column",
              gap: "16px",
              paddingRight: "4px",
            }}>
              {messages.length === 0 && (
                <div style={{ color: colors.textMuted, textAlign: "center", padding: "60px 20px", fontSize: "15px" }}>
                  <div style={{ fontSize: "32px", marginBottom: "12px" }}>Ask me anything</div>
                  <div>Explain a finding · What is SQL injection? · How do I fix XSS?</div>
                  <div style={{ marginTop: "8px" }}>What is CVSS scoring? · How to prioritize remediation?</div>
                </div>
              )}
              {messages.map((m, i) => (
                <div key={i} style={{
                  display: "flex",
                  justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                }}>
                  <div style={{
                    maxWidth: "80%",
                    padding: "12px 16px",
                    borderRadius: m.role === "user" ? "12px 12px 2px 12px" : "12px 12px 12px 2px",
                    background: m.role === "user"
                      ? `linear-gradient(135deg, ${colors.primary}, ${colors.primaryDark})`
                      : colors.bgTertiary,
                    border: m.role === "user"
                      ? "none"
                      : `1px solid ${colors.borderSecondary}`,
                    color: colors.textPrimary,
                    fontSize: "14px",
                    lineHeight: "1.6",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}>
                    {m.content}
                    {m.role === "assistant" && chatStreaming && i === messages.length - 1 && (
                      <span style={{
                        display: "inline-block",
                        width: "8px",
                        height: "14px",
                        background: colors.accent,
                        marginLeft: "2px",
                        verticalAlign: "middle",
                        animation: "blink 1s step-end infinite",
                      }} />
                    )}
                  </div>
                </div>
              ))}
              <div ref={chatBottomRef} />
            </div>

            {/* Input row */}
            <div style={{ borderTop: `1px solid ${colors.borderSecondary}`, paddingTop: "16px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px", cursor: "pointer", color: colors.textSecondary, fontSize: "13px" }}>
                <input
                  type="checkbox"
                  checked={includeFindings}
                  onChange={e => setIncludeFindings(e.target.checked)}
                  style={{ cursor: "pointer" }}
                />
                Include my current findings as context
              </label>
              <div style={{ display: "flex", gap: "8px" }}>
                <input
                  style={{ ...styles.input, flex: 1 }}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="Ask about a vulnerability, finding, or security topic…"
                  onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage()}
                  disabled={chatStreaming}
                />
                <button
                  style={{ ...styles.button, padding: "12px 20px", opacity: chatStreaming ? 0.6 : 1 }}
                  onClick={sendMessage}
                  disabled={chatStreaming}
                >
                  {chatStreaming ? "..." : "Send"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── CODE SCANNER TAB ── */}
        {tab === "code" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* Controls */}
            <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: "16px" }}>
              <div>
                <label style={styles.label}>Language</label>
                <select
                  style={styles.select}
                  value={language}
                  onChange={e => setLanguage(e.target.value)}
                >
                  {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
                </select>
              </div>
              <div>
                <label style={styles.label}>Filename (optional)</label>
                <input
                  style={styles.input}
                  value={filename}
                  onChange={e => setFilename(e.target.value)}
                  placeholder="e.g. auth.py, login.php"
                />
              </div>
            </div>

            {/* Split pane: code input + output */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", alignItems: "start" }}>
              <div>
                <label style={styles.label}>Paste Source Code</label>
                <textarea
                  style={{ ...styles.textarea, height: "420px", fontSize: "13px" }}
                  value={code}
                  onChange={e => setCode(e.target.value)}
                  placeholder="Paste your source code here…"
                  spellCheck={false}
                />
                <button
                  style={{ ...styles.button, width: "100%", marginTop: "12px", opacity: codeStreaming ? 0.6 : 1 }}
                  onClick={analyzeCode}
                  disabled={codeStreaming || !code.trim()}
                >
                  {codeStreaming ? "Analyzing..." : "SCAN FOR VULNERABILITIES"}
                </button>
              </div>

              <div>
                <label style={styles.label}>
                  Security Analysis
                  {codeStreaming && (
                    <span style={{ marginLeft: "8px", color: colors.accent, fontWeight: 400 }}>
                      thinking...
                    </span>
                  )}
                </label>
                <div style={{
                  height: "420px",
                  overflowY: "auto",
                  background: colors.bgSecondary,
                  border: `1px solid ${codeOutput ? colors.borderPrimary : colors.borderSecondary}`,
                  borderRadius: "8px",
                  padding: "16px",
                  fontSize: "13px",
                  lineHeight: "1.7",
                  color: colors.textPrimary,
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                  fontFamily: "inherit",
                  boxShadow: codeOutput ? `0 0 15px rgba(0,102,255,0.2)` : "none",
                }}>
                  {codeOutput || (
                    <span style={{ color: colors.textMuted }}>
                      Analysis will appear here after you click Scan…
                    </span>
                  )}
                  {codeStreaming && (
                    <span style={{
                      display: "inline-block",
                      width: "8px",
                      height: "14px",
                      background: colors.accent,
                      marginLeft: "2px",
                      verticalAlign: "middle",
                      animation: "blink 1s step-end infinite",
                    }} />
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: ${colors.bgSecondary}; }
        ::-webkit-scrollbar-thumb { background: ${colors.borderPrimary}; border-radius: 3px; }
      `}</style>
    </main>
  );
}
