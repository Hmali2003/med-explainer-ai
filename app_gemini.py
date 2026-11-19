import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)  # allows your frontend (different domain) to call this backend

# Each Gemini call gives up after 25 seconds so the request never hangs.
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=25000),
)

# Backup names, used only after the models your key can really use.
BACKUP_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]

_model_cache = []


def get_models():
    """Ask Google which Flash models THIS API key can use (cached). Max 6 models."""
    global _model_cache
    if _model_cache:
        return _model_cache

    found = []
    try:
        for m in client.models.list():
            name = (m.name or "").replace("models/", "")
            actions = getattr(m, "supported_actions", None) or []
            bad = ["image", "tts", "live", "audio", "embedding", "robotics", "computer", "preview"]
            if "flash" in name and "generateContent" in actions and not any(b in name for b in bad):
                found.append(name)
    except Exception:
        pass

    found.sort(reverse=True)  # newest-looking names first
    models = (found + [b for b in BACKUP_MODELS if b not in found])[:6]
    _model_cache = models
    return models


def build_prompt(language):
    lang_instruction = {
        "english": "Respond in simple, plain English.",
        "hindi": "Respond in simple Hindi, written in Devanagari script.",
    }.get(language, "Respond in simple, plain English.")

    return f"""You are a careful medical-label explainer assistant for everyday users
in India who may not read English well or may struggle with a doctor's handwriting.

Look at the attached image of a medicine strip or prescription.

{lang_instruction}

Return ONLY valid JSON in this exact format, nothing else, no markdown fences:
{{
  "medicine_name": "string - the medicine name if identifiable, or 'unclear' if not",
  "purpose": "string - plain-language explanation of what it's generally used for",
  "common_side_effects": ["array", "of", "short strings"],
  "timing": "string - typical timing e.g. 'usually after food, once daily' or 'unclear from image'",
  "warning": "string - always remind the user to confirm with their doctor or pharmacist",
  "clarity": "string - one of: 'clear', 'partially readable', 'unclear' - your honest confidence in reading the image"
}}

Rules:
- If the image is unclear or handwriting is illegible, say so honestly instead of guessing.
- NEVER diagnose a condition or suggest what illness the person has.
- Only explain the medicine itself in general terms.
- Keep language simple, no medical jargon.
- Output must be valid JSON and nothing else - no markdown fences, no extra text.
"""


def call_gemini(prompt, image_bytes, media_type):
    """Go through the models up to 3 rounds, waiting a little between rounds."""
    last_error = None
    for round_no in range(3):
        for model in get_models():
            try:
                return client.models.generate_content(
                    model=model,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=image_bytes, mime_type=media_type),
                    ],
                )
            except Exception as e:
                last_error = e
                msg = str(e)
                if any(c in msg for c in ["404", "NOT_FOUND", "503", "429", "UNAVAILABLE", "timed out", "imeout"]):
                    continue  # try the next model
                raise  # any other error -> stop immediately
        time.sleep(3)  # all models busy -> wait, then try again
    raise last_error


@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    image_bytes = file.read()
    media_type = file.mimetype or "image/jpeg"
    language = request.form.get("language", "english")

    raw_text = ""
    try:
        response = call_gemini(build_prompt(language), image_bytes, media_type)

        raw_text = response.text.strip()
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
        return jsonify(result)

    except json.JSONDecodeError:
        return jsonify({"error": "Could not parse AI response", "raw": raw_text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/models", methods=["GET"])
def list_models():
    """Debug page: shows which models the code will try, in order."""
    return jsonify({"models_tried_in_order": get_models()})


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Medicine Explainer API is running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
