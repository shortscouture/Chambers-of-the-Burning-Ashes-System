from openai import OpenAI
import environ
import os
from pathlib import Path
from tenacity import (
    retry, stop_after_attempt, wait_random_exponential,
)

env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)

BASE_DIR = Path(__file__).resolve().parent.parent
# Read env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

#secret key
OPENAI_KEY = env("OPENAI_API_KEY")
client = OpenAI()


@retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(2))
def completion_with_backoff(**kwargs):
  return client.completions.create(**kwargs)

completion_with_backoff(model="gpt-3.5-turbo", prompt="Once upon a time,", max_tokens=20)
