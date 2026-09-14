import os
import sys
import time
import threading
import requests
from dotenv import load_dotenv
from flask import Flask, request

# تأمين المسار الرئيسي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from telegram_bot import send_telegram_message
import run_pipeline
from video_engine.generator import VideoProductionEngine
from tiktok_uploader import upload_video_to_tiktok

load_dotenv()

TOKEN = "8960674717:AAFvKIoHB4Ajz7h2rt2sqO2tDRFkipbkinw"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

TEMP_STORAGE = {"latest_video_path": None, "latest_title": None, "latest_video_url": None}
PROCESSED_UPDATES = set()

@app.route('/')
def home():
    return "Raseen PRO Cloud-Linked Engine is Live!", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    json_data = request.get_json()
    if json_data:
        update_id = json_data.get("update_id")
        if update_id in PROCESSED_UPDATES:
            return "OK", 200
        PROCESSED_UPDATES.add(update_id)
        if len(PROCESSED_UPDATES) > 100:
            PROCESSED_UPDATES.pop()

        threading.Thread(target=handle_update_safely, args=(json_data,), daemon=True).start()
    return "OK", 200

def upload_to_free_cloud(file_path):
    """رفع الفيديو لسحابة مجانية مؤقتة لتوليد رابط تحميل ومعاينة مباشر"""
    try:
        url = "https://catbox.moe/user/api.php"
        with open(file_path, 'rb') as f:
            files = {'fileToUpload': f}
            data = {'reqtype': 'fileupload'}
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200 and response.text.startswith('http'):
                return response.text.strip()
    except Exception as e:
        print(f"⚠️ Cloud Upload Error: {e}")
    return None

def handle_update_safely(update):
    try:
        if "callback_query" in update:
            query = update["callback_query"]
            data = query.get("data")
            callback_query_id = query.get("id")

            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": callback_query_id})

            if data == "approve_publish":
                video_path = TEMP_STORAGE.get("latest_video_path")
                title = TEMP_STORAGE.get("latest_title", "Raseen Video")

                if video_path and os.path.exists(video_path):
                    send_telegram_message("📤 جاري رفع الفيديو إلى تيك توك...")
                    success = upload_video_to_tiktok(video_path, title=title, auto_publish=False)
                    if success:
                        send_telegram_message(f"✅ **تم النشر بنجاح!**\nفيديو (*{title}*) جاهز في TikTok Inbox.")
                    else:
                        send_telegram_message("❌ فشل الرفع إلى تيك توك.")
                else:
                    send_telegram_message("⚠️ مسار الفيديو غير موجود، يرجى إعادة الطلب.")

            elif data == "edit_script":
                send_telegram_message("✍️ أرسل التعديل أو العنوان الجديد في رسالة وسأقوم بإعادة توليده فوراً.")

            elif data == "cancel_publish":
                TEMP_STORAGE["latest_video_path"] = None
                TEMP_STORAGE["latest_video_url"] = None
                send_telegram_message("❌ تم إلغاء العملية.")
            return

        message = update.get("message", {})
        text = message.get("text", "").strip()
        chat_id = str(message.get("chat", {}).get("id"))

        if CHAT_ID and chat_id != str(CHAT_ID):
            return

        if not text:
            return

        idea_title = text.replace("/create", "").strip()
        if not idea_title or text == "/start":
            send_telegram_message(
                "👋 **أهلاً بك في رصين PRO**\n\n"
                "💡 أرسل فكرة الفيديو وسأقوم بتوليدها، رفعها للسحابة، وإرسال رابط المعاينة وأزرار التحكم."
            )
            return

        send_telegram_message(f"⏳ **[جاري العمل والرفع]**\nجاري إنتاج الفيديو ورفعه للسحابة لفكرة:\n*{idea_title}*\n*(يرجى الانتظار دقيقة حتى يكتمل الرفع...)*")

        # توليد الفيديو
        video_path = None
        try:
            pipeline_func = getattr(run_pipeline, 'run_raseen_pipeline', None) or getattr(run_pipeline, 'run_pipeline', None)
            if pipeline_func:
                res = pipeline_func(
                    topic_title=idea_title,
                    raw_content=f"محتوى: {idea_title}",
                    source_platform="Telegram",
                    engagement_score=98,
                    is_emergency=True
                )
                if isinstance(res, dict):
                    video_path = res.get("video_path")
        except Exception as e:
            print(f"⚠️ Pipeline Error: {e}")

        if not video_path or not os.path.exists(str(video_path)):
            try:
                engine = VideoProductionEngine()
                prod_res = engine.generate_video_assets(script_title=idea_title, script_body=idea_title)
                if isinstance(prod_res, dict):
                    video_path = prod_res.get("video_path")
            except Exception as e:
                print(f"⚠️ Engine Error: {e}")

        if video_path and os.path.exists(str(video_path)):
            # رفع الفيديو للسحابة المجانية للحصول على رابط مباشر
            send_telegram_message("☁️ جاري رفع الفيديو إلى السحابة لتوليد رابط المعاينة...")
            video_url = upload_to_free_cloud(str(video_path))

            TEMP_STORAGE["latest_video_path"] = str(video_path)
            TEMP_STORAGE["latest_title"] = idea_title
            TEMP_STORAGE["latest_video_url"] = video_url

            keyboard_buttons = [
                [
                    {"text": "✅ موافقة ونشر", "callback_data": "approve_publish"},
                    {"text": "✏️ تعديل", "callback_data": "edit_script"}
                ],
                [
                    {"text": "❌ إلغاء", "callback_data": "cancel_publish"}
                ]
            ]

            # إذا تم توليد الرابط بنجاح، نضيف زر معاينة مباشرة
            if video_url:
                keyboard_buttons.insert(0, [{"text": "👀 معاينة وتحميل الفيديو", "url": video_url}])

            keyboard = {"inline_keyboard": keyboard_buttons}
            
            payload = {
                "chat_id": chat_id,
                "text": f"🎬 **تم إنتاج الفيديو ورفعه بنجاح!**\nالعنوان: *{idea_title}*\n\nاختر الإجراء المطلوب:",
                "parse_mode": "Markdown",
                "reply_markup": keyboard
            }
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
        else:
            send_telegram_message("❌ فشل توليد الفيديو، يرجى مراجعة سجلات Render.")

    except Exception as e:
        print(f"⚠️ Critical Error: {e}")

def auto_set_webhook():
    time.sleep(3)
    webhook_url = "https://raseen-content-brain.onrender.com/webhook"
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
    except Exception:
        pass

if __name__ == "__main__":
    threading.Thread(target=auto_set_webhook, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
