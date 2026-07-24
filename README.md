# 💊 MedExplain AI

An AI-powered web app that explains any medicine strip or prescription photo in
plain language — built for people who struggle to read handwritten prescriptions
or unfamiliar medicine names, especially elderly or non-English-comfortable users.

**Live demo:mediscan-ai-scanner.netlify.app
**Backend API:(https://med-explainer-ai.onrender.com)

---

## Problem

Many people in India — especially elderly patients or those less comfortable with
English/medical terminology — struggle to understand what a prescribed medicine is
for, its side effects, or how to take it. Doctor handwriting makes this worse.

## Solution

Upload a photo, or capture one live via camera, and the app uses Google's Gemini
Vision AI to read the label/handwriting and explain it in simple language —
in English or Hindi — including an honest confidence flag on how clearly it
could read the image.

---

## Features

- 📷 **Photo upload or live camera capture** — no need for a separate scanner
- 🌐 **Bilingual output** — English or Hindi
- 🎯 **Plain-language breakdown** — purpose, side effects, timing
- 🩺 **Honest clarity flag** — tells you if the image was hard to read instead of guessing
- 🔊 **Read Aloud** — accessibility-friendly text-to-speech
- ⬇️ **Download as PDF** — save or share the result
- 🕘 **Scan history** — revisit past results (stored locally in your browser)
- 🌙 **Dark mode**
- ⚠️ Always includes a disclaimer to consult a doctor/pharmacist — this is an
  informational tool, not a diagnostic one

---

## Tech Stack

- **Frontend:** HTML, CSS, vanilla JavaScript (no framework — fast and dependency-light)
- **Backend:** Flask (Python)
- **AI:** Google Gemini API (vision + language understanding)
- **Deployment:** Render (backend), Netlify (frontend)
- **Version control:** Git + GitHub

---

## Architecture

```
User's browser (index.html)
        │
        │  photo + language choice
        ▼
Flask backend (app_gemini.py) — hosted on Render
        │
        │  image + prompt
        ▼
Gemini Vision API
        │
        │  structured JSON response
        ▼
Rendered result card in browser
```

---

## Running it locally

1. Clone this repo:
   ```
   git clone https://github.com/Hmali2003/med-explainer-ai.git
   cd med-explainer-ai
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Get a free Gemini API key from [aistudio.google.com](https://aistudio.google.com)
4. Set it as an environment variable:
   ```
   $env:GEMINI_API_KEY="your-key-here"
   ```
5. Run the backend:
   ```
   python app_gemini.py
   ```
6. Open `index.html` in your browser (make sure `BACKEND_URL` in the script points
   to `http://localhost:5000/analyze` for local testing)

---

## Deployment

- **Backend:** deployed on Render as a Python web service (`gunicorn app_gemini:app`),
  with `GEMINI_API_KEY` set as an environment variable
- **Frontend:** static `index.html` deployed on Netlify, pointing to the live Render URL

---

## Design decisions worth mentioning

- **No diagnosis, ever.** The prompt explicitly instructs the model to explain the
  medicine only, never guess at the user's condition — a deliberate safety boundary.
- **Clarity over confidence.** Rather than always giving a confident-sounding answer,
  the app asks the model to flag when an image is genuinely hard to read, and
  surfaces that to the user instead of hiding uncertainty.
- **Free-tier friendly.** Built entirely on free tools (Gemini free tier, Render
  free tier, Netlify free tier) — intentional, since this was built as a student
  project with zero budget.

## What I'd improve next

- Support more Indian languages (Marathi, Tamil, etc.)
- Add user accounts so history syncs across devices instead of staying local
- Add a simple rate-limit/queue to handle Render's free-tier cold start delay
- OCR pre-check before sending to the API, to fail faster on unreadable images

---

## Disclaimer

This tool provides general informational content only and is not a substitute
for professional medical advice. Always consult a doctor or pharmacist before
making decisions about medication.

---

Built by Harsh Mali — MCA student, K.K. Wagh Institute of Engineering, Nashik.
