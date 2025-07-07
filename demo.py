from together import Together

client = Together(api_key="e19e060328b8dfb73b00bff5908a882fe9165df55ffc361f34a651d03cd03c2d")
# e19e060328b8dfb73b00bff5908a882fe9165df55ffc361f34a651d03cd03c2d# 1. Set your API key
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-VL-72B-Instruct",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Extract only the CAPTCHA code from this image. Return just the text (no extra description)."},
            {"type": "image_url", "image_url": {"url": "https://d52c-103-83-219-43.ngrok-free.app/captcha.png"}}
        ]
    }]
)

captcha_code = response.choices[0].message.content.strip()
print("CAPTCHA:", captcha_code)
