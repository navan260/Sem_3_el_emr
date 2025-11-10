import google.generativeai as genai
import json
import re
import mimetypes
import os

# 🔹 Configure Gemini
genai.configure(api_key="AIzaSyD682mjMvDFQCfiqof2BER5aI0MmjlERR0")

# 🔹 Input file path (image or PDF)
file_path = r"C:\Users\Chidanand\Downloads\report.png"

# 🔹 Detect MIME type automatically (image/png, image/jpeg, application/pdf, etc.)
mime_type, _ = mimetypes.guess_type(file_path)

if mime_type is None:
    # Default to binary stream if unknown
    mime_type = "application/octet-stream"

print(f"Detected MIME type: {mime_type}")

# 🔹 Read the file as bytes
with open(file_path, "rb") as f:
    file_data = f.read()

# 🔹 Define prompt
prompt = """
Extract all text content from this file and return it as JSON.
If any field is missing or unknown, use empty string ("").
The JSON should have this structure:
{
  "patient-id": "<id of the patient>",
  "patient-name": "<name of the patient>",
  "phone-number": "<phone number of the patient>",
  "patient-email": "<email>",
  "patient-address": "<address>",
  "disease-name": "<name of the disease>"
}
"""

# 🔹 Use Gemini 1.5 Pro / 1.5 Flash (supports PDFs + Images)
model = genai.GenerativeModel("gemini-2.5-pro")

# 🔹 Generate content
response = model.generate_content(
    [prompt, {"mime_type": mime_type, "data": file_data}]
)

# 🔹 Get model output
raw_output = response.text.strip()
print("RAW OUTPUT FROM GEMINI:\n", raw_output)

# 🔹 Clean out code fences like ```json ... ```
cleaned = re.sub(r"```json|```", "", raw_output).strip()

# 🔹 Try parsing the JSON safely
try:
    actual_json = json.loads(cleaned)
except json.JSONDecodeError:
    print("\n⚠️ Could not parse JSON. Here's the raw cleaned output:")
    print(cleaned)
    exit(1)

# ✅ Done — output structured JSON
print("\n✅ Parsed JSON:")
print(json.dumps(actual_json, indent=2))
