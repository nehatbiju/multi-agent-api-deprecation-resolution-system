import json
import time
from datetime import datetime
from google import genai
from config import GEMINI_API_KEY
from models import DeprecationNotice


# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def extract_deprecation(email_text: str):
    """
    Uses Gemini to extract structured deprecation info.
    Returns DeprecationNotice or None.
    Includes quota-safe backoff handling.
    """

    prompt = f"""
You are an API deprecation detection system.

From the email below, extract:

- provider
- old_api_name
- new_api_name
- deadline (format: YYYY-MM-DD)
- breaking_changes (list of short strings)

If no deprecation exists, return EXACTLY: NONE

Return ONLY valid JSON. No explanation.

EMAIL:
{email_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # If Gemini explicitly says NONE
        if text == "NONE":
            return None

        # Remove markdown code block formatting if present
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        data = json.loads(text)

        return DeprecationNotice(
            provider=data["provider"],
            old_api_name=data["old_api_name"],
            new_api_name=data["new_api_name"],
            deadline=datetime.strptime(
                data["deadline"], "%Y-%m-%d"
            ).date(),
            breaking_changes=data["breaking_changes"]
        )

    except Exception as e:
        error_message = str(e)

        # 🔥 Handle quota exhaustion properly
        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            print("⚠️ Gemini quota exceeded. Backing off for 120 seconds...")
            time.sleep(120)
            return None

        # Handle invalid JSON safely
        if "Expecting value" in error_message or "JSON" in error_message:
            print("⚠️ Gemini returned invalid JSON. Skipping.")
            return None

        print("Gemini extraction failed:", e)
        return None