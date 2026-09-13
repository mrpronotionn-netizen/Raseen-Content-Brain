import os
import sys
import time
import threading
import schedule
import requests
from dotenv import load_dotenv
from flask import Flask, request

# تأمين المسار الرئيسي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from telegram_bot import send_telegram_message
import run_pipeline
from run_pipeline import run_background_research, process_daily_scheduled_video
from video_engine.generator import VideoProductionEngine
from tiktok_uploader import upload_video_to_tiktok

load_dotenv()

CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 1. إنشاء خادم Flask لاستقبال رنين UptimeRobot وتحديثات تيليجرام
app = Flask(__name__)

@app.route('/')
def home():
    return "Raseen PRO Engine is Alive 24/7!", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """استقبال تحديثات تيليجرام ومعالجتها وإرسال رد مباشر"""
    json_data = request.get_json()
    if json_data:
        try:
            message = json_data.get("message", {})
            text = message.get("text", "").strip()
            chat_id = message.get("chat", {}).get("id")
            
            if text and chat_id:
                print(f"📥 [الرسالة المستلمة]: {text}")
                threading.Thread(target=process_single_update, args=(json_data,), daemon=True).start()
        except Exception as e:
            print(f"⚠️ [Webhook Error]: {e}")
    return "OK", 200

def process_single_update(update):
    """معالجة رسالة مفردة قادمة من الويب هوك وتشغيل خط الإنتاج"""
    message = update.get("message", {})
    text = message.get("text", "").strip()
    chat_id = str(message.get("chat", {}).get("id"))

    if CHAT_ID and chat_id != str(CHAT_ID):
        return

    if text:
        idea_title = text.replace("/create", "").strip()
        if not idea_title or text == "/start":
            send_telegram_message(
                "👋 **أهلاً بك في نظام رصين PRO للتحكم الذكي**\n\n"
                "💡 أرسل لي أي فكرة مباشرة وسأقوم بإنتاجها ورفعها لـ TikTok Inbox فوراً!"
            )
            return

        send_telegram_message(f"⚡ **[طلب يدوي مقبول]**\nجاري تشغيل خط الإنتاج لفكرتك:\n*{idea_title}*")

        pipeline_func = getattr(run_pipeline, 'run_raseen_pipeline', None) or getattr(run_pipeline, 'run_pipeline', None)
        
        pipeline_result = {}
        if pipeline_func:
            pipeline_result = pipeline_func(
                topic_title=idea_title,
                raw_content=f"محتوى مخصص تم طلبه يدويًا من التلغرام: {idea_title}",
                source_platform="Telegram Direct Command",
                engagement_score=98,
                is_emergency=True
            )

        video_path = pipeline_result.get("video_path") if isinstance(pipeline_result, dict) else None
        if not video_path:
            print("🎬 [Direct Trigger] جاري إنتاج أصول الفيديو مباشرة...")
            video_engine = VideoProductionEngine()
            prod_res = video_engine.generate_video_assets(script_title=idea_title, script_body=idea_title)
            video_path = prod_res.get("video_path")

        if video_path and os.path.exists(video_path):
            send_telegram_message("📤 جاري رفع الفيديو كمسودة إلى TikTok Inbox...")
            upload_success = upload_video_to_tiktok(video_path, title=idea_title, auto_publish=False)
            
            if upload_success:
                send_telegram_message(f"✅ **تم بنجاح!**\nتم رفع فيديو: *{idea_title}*\nتفقّد **TikTok Inbox** في حسابك الآن.")
            else:
                send_telegram_message("❌ حدث خطأ أثناء عملية الرفع إلى TikTok.")
        else:
            send_telegram_message("❌ تعذر توليد ملف الفيديو، يرجى مراجعة سجل النظام.")

def run_scheduler_loop():
    """تشغيل المجدول الزمني في خلفية النظام"""
    schedule.every(3).hours.do(run_background_research)
    schedule.every().day.at("19:30").do(process_daily_scheduled_video)
    
    print("⏰ [Scheduler] المجدول الزمني يعمل بنجاح في الخلفية...")
    while True:
        schedule.run_pending()
        time.sleep(30)

def auto_set_webhook():
    """تفعيل الويب هوك تلقائياً مع تيليجرام عند بدء التشغيل"""
    time.sleep(3)
    token = "8960674717:AAFvKIoHB4Ajz7h2rt2sqO2tDRFkipbkinw"
    webhook_url = "https://raseen-content-brain.onrender.com/webhook"
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}")
        print(f"🔗 [Webhook Setup]: {response.text}")
    except Exception as e:
        print(f"⚠️ [Webhook Setup Error]: {e}")

if __name__ == "__main__":
    print("🚀 [Raseen Core] تم تشغيل المحرك الرئيسي بنجاح عبر Webhook...")
    
    # 2. تشغيل المجدول في الخفاء
    scheduler_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
    scheduler_thread.start()

    # تفعيل الويب هوك تلقائياً في الخلفية
    threading.Thread(target=auto_set_webhook, daemon=True).start()

    # 3. تشغيل خادم Flask واستقبال الرسائل فوراً
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
