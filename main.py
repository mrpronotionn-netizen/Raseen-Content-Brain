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

# تخزين مؤقت لإدارة الحالة والأزرار
TEMP_STORAGE = {"latest_video_path": None, "latest_title": None}

@app.route('/')
def home():
    return "Raseen PRO Interactive Engine is Alive!", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    json_data = request.get_json()
    if json_data:
        threading.Thread(target=process_telegram_update, args=(json_data,), daemon=True).start()
    return "OK", 200

def process_telegram_update(update):
    try:
        # 1. التعامل مع الأزرار التفاعلية
        if "callback_query" in update:
            query = update["callback_query"]
            data = query.get("data")
            callback_query_id = query.get("id")
            chat_id = str(query["message"]["chat"]["id"])

            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": callback_query_id})

            if data == "approve_publish":
                video_path = TEMP_STORAGE.get("latest_video_path")
                title = TEMP_STORAGE.get("latest_title", "Raseen Video")

                if video_path and os.path.exists(video_path):
                    send_telegram_message("📤 جاري رفع الفيديو الآن إلى تيك توك...")
                    success = upload_video_to_tiktok(video_path, title=title, auto_publish=False)
                    if success:
                        send_telegram_message(f"✅ **تم النشر بنجاح!**\nفيديو (*{title}*) جاهز في TikTok Inbox.")
                    else:
                        send_telegram_message("❌ فشل الرفع إلى تيك توك.")
                else:
                    send_telegram_message("⚠️ ملف الفيديو غير موجود على السيرفر، يرجى إعادة الإنتاج.")

            elif data == "edit_script":
                send_telegram_message("✍️ يرجى إرسال الفكرة أو التعديل الجديد بالرد المباشر، وسأقوم بإعادة توليد الفيديو فوراً بناءً عليها.")

            elif data == "cancel_publish":
                TEMP_STORAGE["latest_video_path"] = None
                send_telegram_message("❌ **تم إلغاء العملية وحذف المسار المؤقت.**")
            return

        # 2. استقبال الرسائل والأفكار
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
                "💡 أرسل لي أي فكرة وسأقوم بمعالجتها وإنتاج الفيديو بالكامل ثم أرسل لك أزرار التحكم."
            )
            return

        send_telegram_message(f"⏳ **[جاري العمل الفعلي]**\nيتم الآن توليد وإنتاج أصول الفيديو لفكرة:\n*{idea_title}*\n*(قد تستغرق العملية دقيقة أو دقيقتين، يرجى الانتظار...)*")

        # تشغيل البايبرلاين والانتظار حتى انتهاء التوليد الحقيقي
        pipeline_func = getattr(run_pipeline, 'run_raseen_pipeline', None) or getattr(run_pipeline, 'run_pipeline', None)
        pipeline_result = {}
        if pipeline_func:
            pipeline_result = pipeline_func(
                topic_title=idea_title,
                raw_content=f"محتوى مخصص: {idea_title}",
                source_platform="Telegram Dashboard",
                engagement_score=98,
                is_emergency=True
            )

        video_path = pipeline_result.get("video_path") if isinstance(pipeline_result, dict) else None
        if not video_path:
            video_engine = VideoProductionEngine()
            prod_res = video_engine.generate_video_assets(script_title=idea_title, script_body=idea_title)
            video_path = prod_res.get("video_path")

        # التحقق الحقيقي من أن الفيديو تم إنشاؤه وموجود على المسار
        if video_path and os.path.exists(video_path):
            TEMP_STORAGE["latest_video_path"] = video_path
            TEMP_STORAGE["latest_title"] = idea_title

            # إرسال الأزرار التفاعلية الثلاثة (موافقة، تعديل، إلغاء)
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ موافقة ونشر", "callback_data": "approve_publish"},
                        {"text": "✏️ تعديل السكربت", "callback_data": "edit_script"}
                    ],
                    [
                        {"text": "❌ إلغاء وحذف", "callback_data": "cancel_publish"}
                    ]
                ]
            }
            
            payload = {
                "chat_id": chat_id,
                "text": f"🎬 **تم إنتاج الفيديو بنجاح تام!**\nالعنوان: *{idea_title}*\n\nاختر الإجراء المطلوب:",
                "parse_mode": "Markdown",
                "reply_markup": keyboard
            }
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
        else:
            send_telegram_message("❌ فشل عملية توليد الفيديو أو أن الملف غير موجود. يرجى مراجعة سجلات Render.")

    except Exception as e:
        print(f"⚠️ [Error]: {e}")
        send_telegram_message(f"⚠️ حدث خطأ تقني أثناء المعالجة: {str(e)}")

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
