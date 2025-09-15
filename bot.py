import os
import time
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

AVATAR_ID = "avatar-xxx"  # استبدل بـ Avatar ID من HeyGen
VOICE_ID = "voice-xxx"    # استبدل بـ Voice ID من HeyGen

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("✍️ اكتب وصف للفيديو بعد الأمر /video")
        return

    await update.message.reply_text("⏳ جاري إنشاء الفيديو...")

    url_generate = "https://api.heygen.com/v2/video/generate"
    payload = {
        "video_inputs": [
            {
                "character": {"type": "avatar", "avatar_id": AVATAR_ID, "avatar_style": "normal"},
                "voice": {"type": "text", "input_text": prompt, "voice_id": VOICE_ID},
                "background": {"type": "color", "value": "#000000"}
            }
        ],
        "dimension": {"width": 1280, "height": 720}
    }
    headers = {"X-Api-Key": HEYGEN_API_KEY, "Content-Type": "application/json"}
    resp = requests.post(url_generate, json=payload, headers=headers)

    if resp.status_code != 200:
        await update.message.reply_text(f"❌ خطأ API: {resp.status_code}")
        return

    video_id = resp.json().get("data", {}).get("video_id")
    if not video_id:
        await update.message.reply_text("❌ لم أستطع الحصول على video_id")
        return

    status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    for _ in range(20):
        time.sleep(6)
        st = requests.get(status_url, headers=headers).json()
        state = st.get("data", {}).get("status")
        if state == "completed":
            video_url = st.get("data", {}).get("result_url")
            await update.message.reply_video(video_url)
            return
        elif state == "failed":
            await update.message.reply_text("❌ فشل إنشاء الفيديو")
            return

    await update.message.reply_text("⌛ الفيديو استغرق وقت طويل. حاول مرة أخرى.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("video", video_command))
    app.run_polling()

if __name__ == "__main__":
    main()
