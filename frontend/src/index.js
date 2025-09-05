console.log("[DEBUG] Index.js starting to load");

import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { Toaster } from "./components/ui/sonner";

console.log("[DEBUG] All imports loaded, about to install unified sender");

// Install global unified sender BEFORE rendering - eliminates race conditions
if (typeof window !== "undefined") {
  console.log("[DEBUG] Window is available, checking for unified sender");
  // Idempotent install
  if (typeof window.unifiedCoachSend !== "function") {
    console.log("[DEBUG] Installing unified sender function");
    window.unifiedCoachSend = async function unifiedCoachSend(text) {
      console.log("[UNIFIED] Sending message:", text);
      
      // Import API functions dynamically
      const { sendCoachMessage } = await import("./apiClient");
      
      // Simple direct call - all logic centralized in apiClient
      return await sendCoachMessage(text); // <- must return
    };
    console.log("[WIRE] Global unified sender installed at bootstrap");
  } else {
    console.log("[DEBUG] Unified sender already exists");
  }
} else {
  console.log("[DEBUG] Window not available");
}

console.log("[DEBUG] About to create React root and render");

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <>
    <App />
    <Toaster />
  </>,
);

console.log("[DEBUG] React app rendered");
