from openai import OpenAI
import environ
import os


env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)


# Read env file
environ.Env.read_env(os.path.join('.env'))

#secret key
OPENAI_KEY = env("OPEN_AI_API_KEY")
client = OpenAI()


completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)

