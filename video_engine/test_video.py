import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from video_engine.generator import VideoProductionEngine
except ModuleNotFoundError:
    from generator import VideoProductionEngine

print("\n=== RASEEN VIDEO PRODUCTION ENGINE TEST ===")

producer = VideoProductionEngine()

# تجربة إنتاج فيديو لسكريبت معتمد
production_result = producer.generate_video_assets(
    script_title="أفضل 3 تطبيقات ذكاء اصطناعي للإنتاجية",
    script_body="هل تعلم أن الذكاء الاصطناعي يوفر عليك ساعتين يومياً؟..."
)

print("\nPRODUCTION RESULT:")
print("مسار الفيديو النهائي:", production_result["video_path"])
print("نتيجة الذاكرة:", production_result["memory_result"])

print("\n=== VIDEO PRODUCTION ENGINE TEST FINISHED ===")