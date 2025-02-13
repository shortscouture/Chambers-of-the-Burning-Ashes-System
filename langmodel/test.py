from openai import OpenAI
import environ
import os
from pathlib import Path


env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Read env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

#secret key
OPENAI_KEY = env("OPENAI_API_KEY")
client = OpenAI()


completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)

