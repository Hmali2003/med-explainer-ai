# Medicine Explainer — Setup & Deployment Guide

## What this is
Upload a photo of a medicine strip or prescription → Claude reads it and explains
purpose, side effects, and timing in plain language.

---

## PART 1 — Run it on your laptop (today, ~30 min)

### Step 1: Open the project in Cursor
1. Open Cursor
2. File → Open Folder → select the `med-explainer` folder
3. Open the built-in terminal in Cursor (Ctrl + `)

### Step 2: Install Python dependencies
In the Cursor terminal, run:
```
pip install -r requirements.txt
```
If you don't have Python installed, download it from python.org first
(check "Add Python to PATH" during install).

### Step 3: Get your Anthropic API key
1. Go to https://console.anthropic.com
2. Sign up / log in
3. Go to "API Keys" → "Create Key"
4. Copy the key (starts with `sk-ant-...`)
5. Add a small amount of credit if prompted (a few dollars is enough for testing)

### Step 4: Set your API key as an environment variable
In the Cursor terminal:

**Windows (PowerShell):**
```
$env:ANTHROPIC_API_KEY="paste-your-key-here"
```

**Mac/Linux:**
```
export ANTHROPIC_API_KEY="paste-your-key-here"
```

⚠️ Never paste your key directly into app.py or commit it to GitHub.

### Step 5: Run the backend
```
python app.py
```
You should see: `Running on http://127.0.0.1:5000`
Keep this terminal open.

### Step 6: Open the frontend
In Cursor's file explorer, right-click `index.html` → "Open with Live Server"
(or just double-click index.html to open it in your browser directly).

### Step 7: Test it
1. Upload a photo of any medicine strip (a Crocin/Dolo box works fine for testing)
2. Click "Analyze"
3. You should see the result card populate in a few seconds

If it fails: check the Cursor terminal running app.py for the error message.

---

## PART 2 — Deploy it so anyone can use it (later today, ~1 hr)

### Step 1: Push code to GitHub
1. Create a new repo on github.com (e.g. `medicine-explainer`)
2. In Cursor terminal:
```
git init
git add .
git commit -m "Initial commit - medicine explainer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/medicine-explainer.git
git push -u origin main
```

### Step 2: Deploy the backend on Render
1. Go to https://render.com → sign up with GitHub
2. Click "New +" → "Web Service"
3. Connect your `medicine-explainer` repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. Under "Environment Variables", add:
   - Key: `ANTHROPIC_API_KEY`
   - Value: your key
6. Click "Create Web Service"
7. Once deployed, copy the URL Render gives you (e.g. `https://medicine-explainer.onrender.com`)

### Step 3: Point frontend to your live backend
In `index.html`, find this line:
```js
const BACKEND_URL = "http://localhost:5000/analyze";
```
Change it to:
```js
const BACKEND_URL = "https://medicine-explainer.onrender.com/analyze";
```

### Step 4: Deploy the frontend on Netlify
1. Go to https://app.netlify.com
2. Drag and drop your `med-explainer` folder onto the Netlify dashboard
3. Netlify gives you a live URL instantly — that's your working app

### Step 5: Update GitHub with the final frontend change
```
git add .
git commit -m "Point frontend to deployed backend"
git push
```

---

## PART 3 — What to say about it in interviews / resume

- **Problem:** Elderly or non-English-comfortable users often can't read
  prescriptions or understand medicine side effects.
- **Solution:** A vision-AI tool that explains any medicine photo in plain language.
- **Stack:** Flask backend, Claude API (vision) for analysis, vanilla JS frontend,
  deployed on Render + Netlify.
- **What you'd improve next:** add Hindi/Marathi output, save history per user,
  add login (this is a good "future work" answer if asked).

## Safety note (mention this proactively in interviews — it shows judgment)
This tool never diagnoses conditions and always tells the user to confirm with
a doctor or pharmacist. That's a deliberate design choice, not a limitation —
mention it when you demo the project.
