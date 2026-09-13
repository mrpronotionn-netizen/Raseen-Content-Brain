import time
import schedule
from run_pipeline import run_background_research, process_daily_scheduled_video

# 1. دورة البحث والتحليل الخلفي: تعمل كل 3 ساعات لجمع الأفكار فقط
schedule.every(3).hours.do(run_background_research)

# 2. دورة الإنتاج اليومي: تفتح قبل موعد النشر المفضل بـ 30 دقيقة
# افترضنا هنا أن أفضل وقت للنشر هو 8:00 مساءً، لذلك التجهيز يكون 7:30 مساءً
schedule.every().day.at("19:30").do(process_daily_scheduled_video)

print("🤖 [Raseen Content Engine Scheduler Running...]")
print("📍 البحث والتحليل الخلفي: يعمل كل 3 ساعات.")
print("📍 التجهيز لـ TikTok Inbox: يومياً الساعة 7:30 مساءً (قبل النشر بـ 30 دقيقة).")
print("📍 المسار الطارئ: يتفعل فوراً إذا كانت النسبة >= 90%.")

# تشغيل فحص أولي عند البداية
run_background_research()

while True:
    schedule.run_pending()
    time.sleep(60)