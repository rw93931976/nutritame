// src/apiClient.js
import axios from "axios";

export const api = axios.create({
  baseURL: "https://meal-plan-assist.preview.emergentagent.com/api",
});

// Always attach Authorization if we have a token
export function setCoachAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}