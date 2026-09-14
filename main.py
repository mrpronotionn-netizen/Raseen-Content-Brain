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

# تخزين مؤقت لآخر فيديو تم إنتاجه
TEMP_STORAGE = {"latest_video_path": None, "latest_title": None}
# لمنع تكرار معالجة نفس الرسالة
PROCESSED_UPDATES = set()

@app.route('/')
def home():
    return "Raseen PRO Core is Live!", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    json_data = request.get_json()
    if json_data:
        update_id = json_data.get("update_id")
        if update_id in PROCESSED_UPDATES:
            return "OK", 200
        PROCESSED_UPDATES.add(update_id)
        # الاحتفاظ فقط بأحدث 100 رسالة في الذاكرة لمنع الامتلاء
        if len(PROCESSED_UPDATES) > 100:
            PROCESSED_UPDATES.pop()

        threading.Thread(target=handle_update_safely, args=(json_data,), daemon=True).start()
    return "OK", 200

def handle_update_safely(update):
    try:
        # 1. معالجة الضغط على الأزرار
        if "callback_query" in update:
            query = update["callback_query"]
            data = query.get("data")
            callback_query_id = query.get("id")

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
                    send_telegram_message("⚠️ انتهت صلاحية مسار الفيديو على السيرفر، يرجى إعادة الطلب.")

            elif data == "edit_script":
                send_telegram_message("✍️ أرسل التعديل أو العنوان الجديد في رسالة منفصلة وسأقوم بإعادة توليده فوراً.")

            elif data == "cancel_publish":
                TEMP_STORAGE["latest_video_path"] = None
                send_telegram_message("❌ تم إلغاء العملية.")
            return

        # 2. معالجة النصوص الواردة
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
                "👋 **أهلاً بك في نظام رصين PRO**\n\n"
                "💡 أرسل لي فكرة الفيديو وسأقوم بتوليدها ومعالجتها بالكامل ثم أرسل لك أزرار التحكم."
            )
            return

        send_telegram_message(f"⏳ **[بدء المعالجة الحقيقية]**\nجاري الآن هندسة وصنع الفيديو لفكرة:\n*{idea_title}*\n*(يرجى الانتظار، سيتم إرسال الأزرار فور اكتمال الملف)*")

        print(f"🚀 [Pipeline Started] Generating video for: {idea_title}")
        
        # تنفيذ عملية التوليد الفعلي
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

        # طريقة احتياطية للتوليد المباشر إن لم يرجع مسار من البايبرلاين
        if not video_path or not os.path.exists(str(video_path)):
            print("🔄 [Fallback Engine] محاولة التوليد عبر محرك الفيديو المباشر...")
            try:
                engine = VideoProductionEngine()
                prod_res = engine.generate_video_assets(script_title=idea_title, script_body=idea_title)
                if isinstance(prod_res, dict):
                    video_path = prod_res.get("video_path")
            except Exception as e:
                print(f"⚠️ Engine Error: {e}")

        # التحقق النهائي وإرسال الأزرار
        if video_path and os.path.exists(str(video_path)):
            TEMP_STORAGE["latest_video_path"] = str(video_path)
            TEMP_STORAGE["latest_title"] = idea_title

            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ موافقة ونشر", "callback_data": "approve_publish"},
                        {"text": "✏️ تعديل", "callback_data": "edit_script"}
                    ],
                    [
                        {"text": "❌ إلغاء", "callback_data": "cancel_publish"}
                    ]
                ]
            }
            
            payload = {
                "chat_id": chat_id,
                "text": f"🎬 **تم إنتاج الفيديو بنجاح تام!**\nالعنوان: *{idea_title}*\n\nاختر الإجراء:",
                "parse_mode": "Markdown",
                "reply_markup": keyboard
            }
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
            print(f"✅ [Success] Video generated and buttons sent for: {idea_title}")
        else:
            send_telegram_message("❌ فشل توليد الفيديو أو أن الملف الناتج غير موجود. يرجى مراجعة Logs في Render.")
            print(f"❌ [Failed] No valid video path found for: {idea_title}")

    except Exception as e:
        print(f"⚠️ Critical Error in handler: {e}")

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
