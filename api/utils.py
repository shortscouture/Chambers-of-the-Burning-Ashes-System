import openai
from django_project.settings import base

openai.api_key = base.OPEN_AI_API_KEY

def send_code_to_api(code):
    try:
        res = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an experienced programmer."},
                {"role": "user", "content": f"Tell me what language is this code: {code}"},
            ],
        )
        return res.choices[0].message.content
    except ConnectionError as e:
        print(f"An error occurred: {e}")
        return str(e)
