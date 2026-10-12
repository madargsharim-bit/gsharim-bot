import os
import urllib.request
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# הגדרות מפתחות
TELEGRAM_BOT_TOKEN = "8657335457:AAFqkFs5rYKrfvhQGD4aUhw5XU-HvI7V9mQ"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

DOC_ID = "1J64_AscdLxZHfaLvCQwJZNnQGvjT9WfqX3MP0z6mRDY"
EXPORT_URL = f"https://docs.google.com/document/d/{DOC_ID}/export?format=txt"

def get_doc_text():
    try:
        with urllib.request.urlopen(EXPORT_URL) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"שגיאה בקריאת המסמך: {e}")
        return ""

def ask_gemini(user_question):
    knowledge_base = get_doc_text()
    if not knowledge_base:
        return "לא הצלחתי לקרוא את המסמך. ודא שהוא מוגדר כציבורי לצפייה."

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    אתה עוזר חכם של יחידת גשרים. ענה על השאלה של המשתמש אך ורק על סמך ספר היחידה הבא.
    אם התשובה אינה מופיעה במסמך, ענה בדיוק: "אין לי מספיק מידע בספר היחידה כדי לענות על כך."

    [תוכן ספר היחידה]:
    {knowledge_base}

    [שאלת המשתמש]:
    {user_question}
    """
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt
    )
    return response.text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    await update.message.reply_text("מחפש בספר היחידה...")
    answer = ask_gemini(user_question)
    await update.message.reply_text(answer)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("הבוט של טלגרם מופעל ברנדר...")
    application.run_polling()