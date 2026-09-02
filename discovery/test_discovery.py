import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discovery.collector import DiscoveryEngine

print("\n=== RASEEN DISCOVERY ENGINE TEST ===")

engine = DiscoveryEngine()

# 1. اختبار اكتشاف خبر جديد
test_item = engine.discover_item(
    title="إطلاق نموذج ذكاء اصطناعي جديد لرصين",
    content="تم الإعلان عن نموذج حديث يساعد في تحليل البيانات واكتشاف المحتوى بشكل آلي.",
    source_url="https://example.com/ai-news",
    category="tech"
)

print("\nDISCOVERY RESULT:")
print(test_item)

# 2. اختبار منع تكرار نفس الخبر
duplicate_item = engine.discover_item(
    title="إطلاق نموذج ذكاء اصطناعي جديد لرصين",
    content="محتوى مكرر لنفس الخبر.",
    source_url="https://example.com/ai-news",
    category="tech"
)

print("\nDUPLICATE DISCOVERY RESULT:")
print(duplicate_item)

print("\n=== DISCOVERY ENGINE TEST FINISHED ===")