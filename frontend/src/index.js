import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { Toaster } from "./components/ui/sonner";

// Install global unified sender BEFORE rendering - eliminates race conditions
if (typeof window !== "undefined") {
  // Idempotent install
  if (typeof window.unifiedCoachSend !== "function") {
    window.unifiedCoachSend = async function unifiedCoachSend(text) {
      console.log("[WIRE] Bootstrap unified sender called with:", text);
      
      // Import API functions dynamically to avoid issues
      const { api, getOrCreateSessionId, sendCoachMessage } = await import("./apiClient");
      
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
        
        // Ensure disclaimer is accepted first - this fixes the 403 error
        try {
          await api.post("/coach/accept-disclaimer", { user_id: userId });
          console.log("[WIRE] disclaimer acceptance ensured");
        } catch (disclaimerErr) {
          // It's ok if disclaimer is already accepted (409 or similar)
          console.log("[WIRE] disclaimer already accepted or error:", disclaimerErr.response?.status);
        }
        
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
