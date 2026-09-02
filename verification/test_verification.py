import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verification.verifier import VerificationEngine

print("\n=== RASEEN VERIFICATION ENGINE TEST ===")

engine = VerificationEngine()

# 1. اختبار تحقق من موضوع موثوق (نسبة ثقة عالية 90%)
verified_item = engine.verify_item(
    title="إطلاق نموذج ذكاء اصطناعي جديد لرصين",
    confidence_score=0.90,
    verification_notes="تم التأكد من المقال الرسمي والمدونة الرسمية للمشروع."
)

print("\nVERIFIED RESULT:")
print(verified_item)

# 2. اختبار موضوع غير موثوق (نسبة ثقة منخفضة 40%)
rejected_item = engine.verify_item(
    title="شائعة إطلاق نموذج جديد غير معلن",
    confidence_score=0.40,
    verification_notes="مصدر شائعة غير موثوق ولا توجد أوراق رسمية تؤكده."
)

print("\nREJECTED RESULT:")
print(rejected_item)

print("\n=== VERIFICATION ENGINE TEST FINISHED ===")