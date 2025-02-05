import openai
from django.conf import settings

openai.api_key = settings.OPEN_AI_API_KEY

def send_code_to_api(code):
    res = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an experienced programmer."},
            {"role": "user", "content": f"Tell me what language is this code: {code}"},
        ],
    )
    return res.choices[0].message.content
