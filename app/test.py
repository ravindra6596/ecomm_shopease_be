import google.generativeai as genai

from app.config.config import settings

API_KEY = settings.GEMINI_API_KEY

genai.configure(api_key=API_KEY)

print('Gen AI Version:',genai.__version__)

for model in genai.list_models():
    print('Gemini Model:',model.name)