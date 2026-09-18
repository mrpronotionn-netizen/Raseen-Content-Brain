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

import run_pipeline
from video_engine.generator import VideoProductionEngine
from tiktok_uploader import upload_video_to_tiktok

load_dotenv()

TOKEN = "8960674717:AAFvKIoHB4Ajz7h2rt2sqO2tDRFkipbkinw"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1719115694")

app = Flask(__name__)

TEMP_STORAGE = {"latest_video_path": None, "latest_title": None, "waiting_for_edit": False}
PROCESSED_UPDATES = set()

def send_telegram_message(text, chat_id=None, token=None):
    """دالة إرسال محلية داخل main.py لمنع مشاكل الاستيراد نهائياً"""
    bot_token = token or TOKEN
    target_chat = chat_id or CHAT_ID
    if not target_chat:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"⚠️ Telegram Send Error: {e}")

@app.route('/')
def home():
    return "Raseen PRO Lightweight Controller is Alive!", 200

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
                send_telegram_message("✍️ **وضع التعديل مفعل:**\nاكتب التعديل أو التعديلات المطلوبة للفيديو هنا في تيليجرام، وسأقوم فوراً بإعادة صياغته وإنتاجه كمسودة جديدة لتيك توك.")

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
                "👋 **أهلاً بك في رصين PRO (الوضع الخفيف)**\n\n"
                "💡 أرسل فكرة الفيديو وسأقوم بتوليدها ومعالجتها وإرسالها مباشرة إلى مسودات تيك توك، مع إتاحة خيار طلب التعديل من هنا بكل سهولة."
            )
            return

        is_edit_request = TEMP_STORAGE.get("waiting_for_edit", False)
        idea_title = text.replace("/create", "").strip()

        if is_edit_request:
            send_telegram_message(f"🔄 **[تطبيق التعديل وإعادة التوليد]**\nجاري إنشاء نسخة محسنة بناءً على ملاحظاتك:\n*{idea_title}*")
            TEMP_STORAGE["waiting_for_edit"] = False
        else:
            send_telegram_message(f"⏳ **[جاري معالجة الفكرة]**\nجاري إعداد محتوى وفيديو للفكرة:\n*{idea_title}*")

        # معالجة توليد الفيديو بطريقة خفيفة ومستقرة
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

        # رفع المسودة مباشرة إلى تيك توك
        if video_path and os.path.exists(str(video_path)):
            TEMP_STORAGE["latest_video_path"] = str(video_path)
            TEMP_STORAGE["latest_title"] = idea_title

            send_telegram_message("📤 جاري رفع الفيديو كمسودة إلى تيك توك...")
            success = upload_video_to_tiktok(str(video_path), title=idea_title, auto_publish=False)

            if success:
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
                    "text": f"✅ **تم إرسال الفيديو بنجاح إلى TikTok Inbox (مسودة)!**\nالعنوان: *{idea_title}*\n\nيمكنك معاينته من تطبيق تيك توك الآن. إذا أردت تعديله، اضغط على الزر أدناه:",
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
            else:
                send_telegram_message("❌ حدث خطأ أثناء الرفع إلى تيك توك، يرجى المحاولة لاحقاً.")
        else:
            send_telegram_message("❌ تعذر إتمام توليد الفيديو حالياً، يرجى المحاولة بفكرة أخرى.")

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
    app.run(host="0.0.0.0", port=port)import os
import sys
import time
import threading
import requests
from dotenv import load_dotenv
from flask import Flask, request

# تأمين المسار الرئيسي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import run_pipeline
from video_engine.generator import VideoProductionEngine
from tiktok_uploader import upload_video_to_tiktok

load_dotenv()

TOKEN = "8960674717:AAFvKIoHB4Ajz7h2rt2sqO2tDRFkipbkinw"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1719115694")

app = Flask(__name__)

TEMP_STORAGE = {"latest_video_path": None, "latest_title": None, "waiting_for_edit": False}
PROCESSED_UPDATES = set()

def send_telegram_message(text, chat_id=None, token=None):
    """دالة إرسال محلية داخل main.py لمنع مشاكل الاستيراد نهائياً"""
    bot_token = token or TOKEN
    target_chat = chat_id or CHAT_ID
    if not target_chat:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"⚠️ Telegram Send Error: {e}")

@app.route('/')
def home():
    return "Raseen PRO Lightweight Controller is Alive!", 200

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
                send_telegram_message("✍️ **وضع التعديل مفعل:**\nاكتب التعديل أو التعديلات المطلوبة للفيديو هنا في تيليجرام، وسأقوم فوراً بإعادة صياغته وإنتاجه كمسودة جديدة لتيك توك.")

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
                "👋 **أهلاً بك في رصين PRO (الوضع الخفيف)**\n\n"
                "💡 أرسل فكرة الفيديو وسأقوم بتوليدها ومعالجتها وإرسالها مباشرة إلى مسودات تيك توك، مع إتاحة خيار طلب التعديل من هنا بكل سهولة."
            )
            return

        is_edit_request = TEMP_STORAGE.get("waiting_for_edit", False)
        idea_title = text.replace("/create", "").strip()

        if is_edit_request:
            send_telegram_message(f"🔄 **[تطبيق التعديل وإعادة التوليد]**\nجاري إنشاء نسخة محسنة بناءً على ملاحظاتك:\n*{idea_title}*")
            TEMP_STORAGE["waiting_for_edit"] = False
        else:
            send_telegram_message(f"⏳ **[جاري معالجة الفكرة]**\nجاري إعداد محتوى وفيديو للفكرة:\n*{idea_title}*")

        # معالجة توليد الفيديو بطريقة خفيفة ومستقرة
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

        # رفع المسودة مباشرة إلى تيك توك
        if video_path and os.path.exists(str(video_path)):
            TEMP_STORAGE["latest_video_path"] = str(video_path)
            TEMP_STORAGE["latest_title"] = idea_title

            send_telegram_message("📤 جاري رفع الفيديو كمسودة إلى تيك توك...")
            success = upload_video_to_tiktok(str(video_path), title=idea_title, auto_publish=False)

            if success:
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
                    "text": f"✅ **تم إرسال الفيديو بنجاح إلى TikTok Inbox (مسودة)!**\nالعنوان: *{idea_title}*\n\nيمكنك معاينته من تطبيق تيك توك الآن. إذا أردت تعديله، اضغط على الزر أدناه:",
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
            else:
                send_telegram_message("❌ حدث خطأ أثناء الرفع إلى تيك توك، يرجى المحاولة لاحقاً.")
        else:
            send_telegram_message("❌ تعذر إتمام توليد الفيديو حالياً، يرجى المحاولة بفكرة أخرى.")

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