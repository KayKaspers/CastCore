import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import de from "./de.json";
import en from "./en.json";

// Language is chosen in the Setup Wizard and per user; persisted in localStorage.
const stored = typeof localStorage !== "undefined" ? localStorage.getItem("castcore.lang") : null;

void i18n.use(initReactI18next).init({
  resources: {
    de: { translation: de },
    en: { translation: en }
  },
  lng: stored ?? "de",
  fallbackLng: "en",
  interpolation: { escapeValue: false }
});

export function setLanguage(lang: "de" | "en") {
  void i18n.changeLanguage(lang);
  localStorage.setItem("castcore.lang", lang);
  document.documentElement.lang = lang;
}

export default i18n;
