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

TEMP_STORAGE = {"latest_video_path": None, "latest_title": None, "waiting_for_edit": False}
PROCESSED_UPDATES = set()

@app.route('/')
def home():
    return "Raseen PRO TikTok Direct Engine is Alive!", 200

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

def handle_update_safely(update):
    try:
        if "callback_query" in update:
            query = update["callback_query"]
            data = query.get("data")
            callback_query_id = query.get("id")

            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": callback_query_id})

            if data == "edit_script":
                TEMP_STORAGE["waiting_for_edit"] = True
                send_telegram_message("✍️ **وضع التعديل مفعل:**\nاكتب التعديل أو الفكرة الجديدة هنا في تيليجرام، وسأقوم فوراً بإعادة توليد فيديو جديد وإرساله كمسودة لتيك توك.")

            elif data == "cancel_process":
                TEMP_STORAGE["latest_video_path"] = None
                TEMP_STORAGE["waiting_for_edit"] = False
                send_telegram_message("❌ تم إلغاء العملية.")
            return

        message = update.get("message", {})
        text = message.get("text", "").strip()
        chat_id = str(message.get("chat", {}).get("id"))

        if CHAT_ID and chat_id != str(CHAT_ID):
            return

        if not text:
            return

        if text == "/start":
            send_telegram_message(
                "👋 **أهلاً بك في رصين PRO**\n\n"
                "💡 أرسل فكرة الفيديو وسأقوم بتوليدها ورفعها تلقائياً إلى مسودات تيك توك، مع إتاحة خيار التعديل من هنا إذا احتجت لذلك."
            )
            return

        is_edit_request = TEMP_STORAGE.get("waiting_for_edit", False)
        idea_title = text.replace("/create", "").strip()

        if is_edit_request:
            send_telegram_message(f"🔄 **[إعادة التوليد للتعديل]**\nجاري إنتاج فيديو جديد بناءً على طلبك:\n*{idea_title}*")
            TEMP_STORAGE["waiting_for_edit"] = False
        else:
            send_telegram_message(f"⏳ **[جاري العمل الفعلي]**\nجاري إنتاج الفيديو ورفعه مباشرة كمسودة إلى تيك توك لفكرة:\n*{idea_title}*")

        # 1. توليد الفيديو
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

        # 2. الرفع المباشر كمسودة إلى تيك توك
        if video_path and os.path.exists(str(video_path)):
            TEMP_STORAGE["latest_video_path"] = str(video_path)
            TEMP_STORAGE["latest_title"] = idea_title

            send_telegram_message("📤 جاري رفع الفيديو الآن إلى تيك توك (مسودة)...")
            success = upload_video_to_tiktok(str(video_path), title=idea_title, auto_publish=False)

            if success:
                # إرسال رسالة مع أزرار التحكم في حال رغب المستخدم بتعديله وإعادة إرساله
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "✏️ طلب تعديل وإعادة إنتاج", "callback_data": "edit_script"}
                        ],
                        [
                            {"text": "❌ إنهاء", "callback_data": "cancel_process"}
                        ]
                    ]
                }
                payload = {
                    "chat_id": chat_id,
                    "text": f"✅ **تم رفع الفيديو بنجاح إلى TikTok Inbox (مسودة)!**\nالعنوان: *{idea_title}*\n\nيمكنك الآن فتحه من تطبيق تيك توك ومعاينته. إذا أردت تعديله وإعادة إنتاجه، اضغط الزر أدناه:",
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
            else:
                send_telegram_message("❌ فشل الرفع التلقائي إلى تيك توك. يرجى مراجعة السجلات.")
        else:
            send_telegram_message("❌ فشل توليد الفيديو، يرجى مراجعة سجلات النظام.")

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
