import os
import sys

# إضافة مسار جذر المشروع ومسار مجلد scheduler بشكل مباشر لحل تعارض الاستيراد
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from scheduler.scheduler import RaseenScheduler
except ModuleNotFoundError:
    from scheduler import RaseenScheduler

print("\n=== RASEEN SCHEDULER & NOTIFIER TEST ===")

scheduler = RaseenScheduler(check_interval_hours=3, unanswered_timeout_minutes=20)

# 1. تجربة دورة الطوارئ مع عدم الرد (موثوقية > 90% -> نشر تلقائي)
print("\n--- 1. اختبار تريند طارئ (موثوقية 92%) بدون رد ---")
emergency_result = scheduler.process_cycle(is_emergency=True)
print("النتيجة:", emergency_result["action"])

# 2. تجربة دورة روتينية مع عدم الرد (موثوقية < 90% -> تجميد وتحويل لتحليل)
print("\n--- 2. اختبار دورة روتينية (موثوقية 85%) بدون رد ---")
routine_result = scheduler.process_cycle(is_emergency=False)
print("النتيجة:", routine_result["action"])

print("\n=== SCHEDULER & NOTIFIER TEST FINISHED ===")