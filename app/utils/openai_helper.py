# from openai import OpenAI
# from app.config.config import settings
#
# client = OpenAI(
#     api_key=settings.OPENAI_API_KEY
# )
#
#
# def ask_chatbot(message: str):
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "system",
#                 "content": """
#                 You are an ecommerce customer support assistant.
#
#                 Help users with:
#                 - orders
#                 - refunds
#                 - cancellations
#                 - payments
#                 - delivery
#
#                 Keep answers short and helpful.
#                 """
#             },
#             {
#                 "role": "user",
#                 "content": message
#             }
#         ]
#     )
#
#     return response.choices[0].message.content
import google.generativeai as genai
from app.config.config import settings

genai.configure(
    api_key=settings.GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "models/gemini-flash-latest"
)


def ask_chatbot(message: str):

    try:

        response = model.generate_content(
            f"""
                You are an ecommerce support chatbot.

                Help users with:
                - order issues
                - refunds
                - cancellations
                - delivery
                - payments

                Keep responses short and friendly.

                User Message:
                {message}
                """
        )
        print("Gemini Response:", response.text)

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return str(e)