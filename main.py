import os
import sys
import time
import threading
import schedule
from dotenv import load_dotenv

# تأمين المسار الرئيسي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from telegram_bot import handle_incoming_telegram_commands
from run_pipeline import run_background_research, process_daily_scheduled_video

load_dotenv()

def run_scheduler_loop():
    """تشغيل المجدول الزمني في خلفية النظام"""
    schedule.every(3).hours.do(run_background_research)
    schedule.every().day.at("19:30").do(process_daily_scheduled_video)
    
    print("⏰ [Scheduler] المجدول الزمني يعمل بنجاح في الخلفية...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    print("🚀 [Raseen Core] تم تشغيل المحرك الرئيسي (المجدول + بوت التلغرام)...")
    
    # 1. تشغيل المجدول في الخفاء
    scheduler_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
    scheduler_thread.start()

    # 2. تشغيل الاستماع الفوري لأوامر الجوال عبر التلغرام
    handle_incoming_telegram_commands()