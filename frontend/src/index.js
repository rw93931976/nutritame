import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { Toaster } from "./components/ui/sonner";
import { getOrCreateSessionId, sendCoachMessage } from "./apiClient";

// Install global unified sender BEFORE rendering - eliminates race conditions
if (typeof window !== "undefined") {
  // Idempotent install
  if (typeof window.unifiedCoachSend !== "function") {
    window.unifiedCoachSend = async function unifiedCoachSend(text) {
      const body = (text || "").trim();
      if (!body) return;

      const userId =
        window.__state?.userId || localStorage.getItem("nt_coach_user_id");
      if (!userId) {
        console.error("[WIRE] unifiedCoachSend: missing user_id");
        throw new Error("Missing user_id");
      }

      try {
        console.log("[WIRE] unifiedCoachSend start:", body);
        const sessionId = await getOrCreateSessionId(userId);
        console.log("[WIRE] session acquired:", sessionId);
        const result = await sendCoachMessage({ sessionId, message: body });
        console.log("[WIRE] message sent successfully");
        return result;
      } catch (err) {
        console.error("[WIRE] unifiedCoachSend failed:", err?.response?.data || err);
        throw err;
      }
    };
    console.log("[WIRE] Global unified sender installed at bootstrap");
  }
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <>
    <App />
    <Toaster />
  </>,
);
