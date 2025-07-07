# captcha_solver.py

import re
from together import Together

class CaptchaSolver:
    def __init__(self, api_key):
        self.client = Together(api_key=api_key)

    def solve_captcha_from_url(self, image_url):
        try:
            print(f"[INFO] Sending image to Together AI → {image_url}")
            response = self.client.chat.completions.create(
                model="Qwen/Qwen2.5-VL-72B-Instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract only the CAPTCHA code from this image. Return just the text (no extra description)."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }]
            )

            raw_output = response.choices[0].message.content.strip()
            print(f"[AI Raw Output] {raw_output}")

            # Clean the CAPTCHA text (remove symbols, etc.)
            cleaned = re.findall(r'\b[a-zA-Z0-9]{4,10}\b', raw_output)
            return cleaned[0] if cleaned else ""

        except Exception as e:
            print(f"[❌] Error solving CAPTCHA: {e}")
            return ""
