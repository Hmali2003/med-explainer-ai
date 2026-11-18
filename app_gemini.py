import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)  # allows your frontend (different domain) to call this backend

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

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

import time

MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"]

def call_gemini(prompt, image_bytes, media_type):
    last_error = None
    for model in MODELS:
        for attempt in range(2):
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
                if "503" in msg or "429" in msg or "UNAVAILABLE" in msg:
                    time.sleep(2)   # short wait, then retry / try next model
                    continue
                raise               # other errors: stop immediately
    raise last_error
@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    image_bytes = file.read()
    media_type = file.mimetype or "image/jpeg"
    language = request.form.get("language", "english")

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


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Medicine Explainer API is running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
