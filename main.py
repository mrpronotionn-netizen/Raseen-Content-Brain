import os
import sys
import time
import threading
import schedule
import requests
from dotenv import load_dotenv
from flask import Flask

# تأمين المسار الرئيسي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from telegram_bot import handle_incoming_telegram_commands
from run_pipeline import run_background_research, process_daily_scheduled_video

load_dotenv()

# 1. إنشاء خادم Flask لاستقبال رنين UptimeRobot ومنع الخمول على Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Raseen PRO Engine is Alive 24/7!", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """مسار استقبال تحديثات تيليجرام وتوجيهها لمعالجة الرسائل والفيديو"""
    # يمكنك ربط مسار استقبال الستريم أو الأوامر هنا مباشرة مع بوت تيليجرام
    return "OK", 200

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
    time.sleep(3) # الانتظار ثوانٍ ليتم تشغيل السيرفر بالكامل
    token = "8960674717:AAFvKIoHB4Ajz7h2rt2sqO2tDRFkipbkinw"
    webhook_url = "https://raseen-content-brain.onrender.com/webhook"
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}")
        print(f"🔗 [Webhook Setup]: {response.text}")
    except Exception as e:
        print(f"⚠️ [Webhook Error]: {e}")

if __name__ == "__main__":
    print("🚀 [Raseen Core] تم تشغيل المحرك الرئيسي (المجدول + بوت التلغرام + خادم الويب)...")
    
    # 2. تشغيل المجدول في الخفاء
    scheduler_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
    scheduler_thread.start()

    # تفعيل الويب هوك تلقائياً في الخلفية
    threading.Thread(target=auto_set_webhook, daemon=True).start()

    # 3. تشغيل خادم Flask في Thread منفصل لكي لا يمنع بوت التلغرام من العمل
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()

    # 4. تشغيل الاستماع الفوري لأوامر الجوال عبر التلغرام في الخيط الرئيسي
    handle_incoming_telegram_commands()
