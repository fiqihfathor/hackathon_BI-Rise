import React, { useState, useEffect, useRef } from "react";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import CircularProgress from "@mui/material/CircularProgress";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import SendIcon from "@mui/icons-material/Send";
import ReactMarkdown from "react-markdown";

// project imports
import MainCard from "components/MainCard";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      from: "bot",
      text: `Hi there! 👋  
My name is **RISA**. I’m your Fraud Investigator Agent.  
You can send me a **transaction ID** or a **user ID**, and I’ll help you analyze whether it's potentially fraudulent.  
  
Just provide one of the following:  
🔍 A specific transaction to investigate  
🧑‍💼 A user ID to analyze the user’s behavior across multiple transactions  
  
I'll return a recommendation with reasoning, confidence score, and suggested actions.  
  
How can I assist you today?`,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const sessionId = "demo-session-id"; // <- Ganti dengan session ID unik jika perlu

  // Auto-scroll ke bawah setiap kali ada pesan baru
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { from: "user", text: userMessage }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(
        "http://localhost:5678/webhook/6f166918-608d-4204-8650-2346b1ce4936/chat",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chatInput: userMessage, sessionId }),
        }
      );

      const data = await res.json();
      setMessages((prev) => [...prev, { from: "bot", text: data.output }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          from: "bot",
          text: "⚠️ Sorry, something went wrong while processing your request.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <MainCard
    title="RISA (Rise-Assistant)"
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "80vh",
        overflow: "auto"
      }}
    >
      {/* Chat Box */}
      <List
        sx={{
          flexGrow: 1,
          minHeight: 0,
          overflowY: "auto",
          px: 1,
          pb: 1,
        }}
      >
        {messages.map((msg, idx) => (
          <ListItem
            key={idx}
            sx={{
              justifyContent: msg.from === "user" ? "flex-end" : "flex-start",
            }}
          >
            <Box
              sx={{
                bgcolor:
                  msg.from === "user" ? "primary.main" : "grey.100",
                color:
                  msg.from === "user"
                    ? "primary.contrastText"
                    : "text.primary",
                borderRadius: 2,
                px: 2,
                py: 1,
                maxWidth: "75%",
                boxShadow: 1,
                wordBreak: "break-word",
              }}
            >
              {msg.from === "bot" ? (
                <Typography component="div" sx={{ whiteSpace: "normal" }}>
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </Typography>
              ) : (
                <Typography>{msg.text}</Typography>
              )}
            </Box>
          </ListItem>
        ))}
        <div ref={messagesEndRef} />
      </List>

      {/* Input Area */}
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <IconButton
          color="primary"
          onClick={sendMessage}
          disabled={!input.trim() || loading}
          sx={{ ml: 1 }}
          aria-label="send"
        >
          {loading ? <CircularProgress size={24} /> : <SendIcon />}
        </IconButton>
      </Box>
    </MainCard>
  );
}
